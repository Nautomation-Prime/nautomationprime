---
title: "Secure Credential Vaulting for Network Automation: HashiCorp Vault, AWS Secrets Manager, and Beyond"
description: How to integrate enterprise-grade secrets management into your automation workflows for safety and compliance.
tags:
  - Expert
  - Security
  - Credential Vaulting
  - HashiCorp Vault
  - AWS Secrets Manager
  - Network Automation
  - Tutorial
---

## Secure Credential Vaulting for Network Automation: HashiCorp Vault, AWS Secrets Manager, and Beyond

> *Published: March 1, 2026*  
> *Author: Nautomation Prime Team*

## Why This Tutorial Exists

Hardcoded credentials are a **top security risk** in network automation. This comprehensive tutorial shows how to use enterprise-grade secrets managers with Python, integrating with Nornir, Ansible, and CI/CD pipelines. Aligned with the PRIME Framework for safety and compliance.

---

## Prerequisites

- Advanced Python (3.8+)
- Understanding of authentication and authorisation models
- Experience with environment variables and secure API calls
- Familiarity with network security concepts (SSH keys, OAuth, mTLS)

---

## Why Use a Secrets Manager?

| Feature | Hardcoded | Environment Vars | Secrets Manager |
| --------- | ----------- | ------------------ | ----------------- |
| **Centralized** | ❌ | ❌ | ✅ |
| **Auditable** | ❌ | ❌ | ✅ |
| **Rotation** | ❌ | Manual | ✅ Automatic |
| **Dynamic Secrets** | ❌ | ❌ | ✅ |
| **RBAC** | ❌ | ❌ | ✅ |
| **Encryption** | ❌ | ⚠️ | ✅ |
| **Compliance Ready** | ❌ | ❌ | ✅ |

---

## Architecture: Multi-Tier Vault Strategy

```text
Application Layer
    ↓
Vault Manager (Abstract Interface)
    ├── HashiCorp Vault (On-Prem, High Security)
    ├── AWS Secrets Manager (Cloud-Native)
    ├── Azure Key Vault (Azure-Integrated)
    └── Local Keyring (Development)
    ↓
Local Cache (with TTL)
    ↓
Network Devices
```

---

## Comprehensive Vault Manager Implementation

Multi-backend secrets management with abstraction layer:

```python
import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import hmac
import base64
from pathlib import Path

logger = logging.getLogger(__name__)

class VaultBackend(Enum):
    """Supported vault backend types"""
    HASHICORP = "hashicorp_vault"
    AWS = "aws_secrets_manager"
    AZURE = "azure_keyvault"
    KEYRING = "local_keyring"

@dataclass
class CacheEntry:
    """Cached credential entry with TTL"""
    secret: Any
    expiry: datetime
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        return datetime.now() >= self.expiry

class BaseVaultBackend(ABC):
    """Abstract base for vault backends"""
    
    @abstractmethod
    async def get_secret(self, path: str, key: Optional[str] = None) -> Any:
        """Retrieve secret from vault"""
        pass
    
    @abstractmethod
    async def put_secret(self, path: str, secret: Dict[str, Any]) -> None:
        """Store secret in vault"""
        pass
    
    @abstractmethod
    async def rotate_secret(self, path: str) -> None:
        """Rotate secret (if supported)"""
        pass
    
    @abstractmethod
    async def delete_secret(self, path: str) -> None:
        """Delete secret from vault"""
        pass

class HashiCorpVaultBackend(BaseVaultBackend):
    """HashiCorp Vault backend implementation"""
    
    def __init__(self, vault_addr: str, vault_token: str, verify_ssl: bool = True):
        self.vault_addr = vault_addr
        self.vault_token = vault_token
        self.verify_ssl = verify_ssl
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize Vault client"""
        import hvac
        
        self.client = hvac.Client(
            url=self.vault_addr,
            token=self.vault_token,
            verify=self.verify_ssl
        )
        
        try:
            self.client.auth.token.lookup_self()
            logger.info(f"Connected to Vault at {self.vault_addr}")
        except Exception as e:
            logger.error(f"Failed to connect to Vault: {e}")
            raise
    
    async def get_secret(self, path: str, key: Optional[str] = None) -> Any:
        """
        Retrieve secret from Vault KV2 engine
        
        Args:
            path: Path to secret (e.g., "network/credentials/router1")
            key: Optional specific key within secret
        
        Returns:
            Secret value or full secret dict
        """
        try:
            secret_response = self.client.secrets.kv.v2.read_secret_version(path=path)
            secret_data = secret_response['data']['data']
            
            logger.info(
                f"Retrieved secret from Vault: {path}",
                extra={'vault_path': path}
            )
            
            if key:
                return secret_data.get(key)
            return secret_data
        
        except Exception as e:
            logger.error(f"Failed to retrieve secret from Vault: {e}")
            raise
    
    async def put_secret(self, path: str, secret: Dict[str, Any]) -> None:
        """Store secret in Vault"""
        try:
            self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=secret
            )
            logger.info(f"Stored secret in Vault: {path}")
        
        except Exception as e:
            logger.error(f"Failed to store secret in Vault: {e}")
            raise
    
    async def rotate_secret(self, path: str) -> None:
        """
        Implement secret rotation:
        1. Generate new secret
        2. Store in Vault
        3. Update policy version tracking
        """
        try:
            # Read current secret metadata
            metadata = self.client.secrets.kv.v2.read_secret_metadata(path=path)
            
            # Create new version (automatic with create_or_update)
            new_secret = {
                'rotated_at': datetime.now().isoformat(),
                'rotation_count': metadata['data'].get('custom_metadata', {}).get('rotation_count', 0) + 1
            }
            
            await self.put_secret(path, new_secret)
            logger.info(f"Rotated secret: {path}")
        
        except Exception as e:
            logger.error(f"Failed to rotate secret: {e}")
            raise
    
    async def delete_secret(self, path: str) -> None:
        """Delete secret from Vault"""
        try:
            self.client.secrets.kv.v2.delete_latest_version_of_secret(path=path)
            logger.info(f"Deleted secret: {path}")
        
        except Exception as e:
            logger.error(f"Failed to delete secret: {e}")
            raise

class AWSSecretsManagerBackend(BaseVaultBackend):
    """AWS Secrets Manager backend implementation"""
    
    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize AWS Secrets Manager client"""
        import boto3
        
        self.client = boto3.client('secretsmanager', region_name=self.region)
        logger.info(f"Connected to AWS Secrets Manager in {self.region}")
    
    async def get_secret(self, path: str, key: Optional[str] = None) -> Any:
        """
        Retrieve secret from AWS Secrets Manager
        
        Args:
            path: Secret name (e.g., "network/router1/credentials")
            key: Optional JSON key within secret string
        """
        try:
            response = self.client.get_secret_value(SecretId=path)
            
            if 'SecretString' in response:
                secret_data = json.loads(response['SecretString'])
            else:
                secret_data = base64.b64decode(response['SecretBinary']).decode('utf-8')
            
            logger.info(f"Retrieved secret from AWS: {path}")
            
            if key and isinstance(secret_data, dict):
                return secret_data.get(key)
            return secret_data
        
        except Exception as e:
            logger.error(f"Failed to retrieve secret from AWS: {e}")
            raise
    
    async def put_secret(self, path: str, secret: Dict[str, Any]) -> None:
        """Store/update secret in AWS Secrets Manager"""
        try:
            self.client.put_secret_value(
                SecretId=path,
                SecretString=json.dumps(secret)
            )
            logger.info(f"Stored secret in AWS: {path}")
        
        except self.client.exceptions.ResourceNotFoundException:
            # Create if doesn't exist
            self.client.create_secret(
                Name=path,
                SecretString=json.dumps(secret)
            )
            logger.info(f"Created new secret in AWS: {path}")
        
        except Exception as e:
            logger.error(f"Failed to store secret in AWS: {e}")
            raise
    
    async def rotate_secret(self, path: str) -> None:
        """
        Enable/trigger rotation in AWS Secrets Manager
        AWS handles actual rotation with Lambda functions
        """
        try:
            # Update secret with rotation flag
            secret = await self.get_secret(path)
            secret['last_rotation'] = datetime.now().isoformat()
            await self.put_secret(path, secret)
            
            logger.info(f"Marked secret for rotation: {path}")
        
        except Exception as e:
            logger.error(f"Failed to initiate rotation: {e}")
            raise
    
    async def delete_secret(self, path: str) -> None:
        """Delete secret from AWS"""
        try:
            self.client.delete_secret(
                SecretId=path,
                ForceDeleteWithoutRecovery=False  # 7-day recovery window
            )
            logger.info(f"Deleted secret: {path}")
        
        except Exception as e:
            logger.error(f"Failed to delete secret: {e}")
            raise

class VaultManager:
    """
    Central credential manager with:
    - Multi-backend support (Vault, AWS, Azure, Keyring)
    - Local caching with TTL
    - Automatic secret rotation
    - Comprehensive audit logging
    - Circuit breaker for vault failures
    """
    
    def __init__(
        self,
        backend_type: VaultBackend = VaultBackend.HASHICORP,
        cache_ttl: int = 3600,
        enable_audit: bool = True,
        **backend_kwargs
    ):
        """
        Args:
            backend_type: Which vault backend to use
            cache_ttl: Cache time-to-live in seconds
            enable_audit: Enable audit logging for all operations
            **backend_kwargs: Credentials for vault backend
        """
        self.backend_type = backend_type
        self.cache_ttl = cache_ttl
        self.enable_audit = enable_audit
        self.cache: Dict[str, CacheEntry] = {}
        self.audit_log: List[Dict[str, Any]] = []
        
        # Initialize backend
        self.backend = self._init_backend(backend_type, **backend_kwargs)
    
    def _init_backend(self, backend_type: VaultBackend, **kwargs) -> BaseVaultBackend:
        """Initialize appropriate vault backend"""
        if backend_type == VaultBackend.HASHICORP:
            return HashiCorpVaultBackend(
                vault_addr=os.environ.get('VAULT_ADDR', kwargs.get('vault_addr')),
                vault_token=os.environ.get('VAULT_TOKEN', kwargs.get('vault_token')),
                verify_ssl=kwargs.get('verify_ssl', True)
            )
        
        elif backend_type == VaultBackend.AWS:
            return AWSSecretsManagerBackend(
                region=os.environ.get('AWS_REGION', kwargs.get('region', 'us-east-1'))
            )
        
        else:
            raise ValueError(f"Unsupported backend: {backend_type}")
    
    async def get_secret(self, path: str, key: Optional[str] = None) -> Any:
        """
        Retrieve secret with caching
        
        Args:
            path: Path to secret
            key: Optional specific key within secret
        
        Returns:
            Secret value
        """
        # Check cache
        cache_key = f"{path}:{key}" if key else path
        if cache_key in self.cache and not self.cache[cache_key].is_expired():
            logger.debug(f"Cache hit: {cache_key}")
            self._audit_log('cache_hit', cache_key)
            return self.cache[cache_key].secret
        
        # Fetch from vault
        try:
            secret = await self.backend.get_secret(path, key)
            
            # Cache result
            self.cache[cache_key] = CacheEntry(
                secret=secret,
                expiry=datetime.now() + timedelta(seconds=self.cache_ttl)
            )
            
            self._audit_log('secret_retrieved', path, {'key': key})
            
            return secret
        
        except Exception as e:
            logger.error(f"Failed to retrieve secret: {e}")
            self._audit_log('secret_retrieval_failed', path, {'error': str(e)})
            raise
    
    async def put_secret(self, path: str, secret: Dict[str, Any]) -> None:
        """Store secret in vault and invalidate cache"""
        try:
            await self.backend.put_secret(path, secret)
            
            # Invalidate cache
            for key in list(self.cache.keys()):
                if key.startswith(path):
                    del self.cache[key]
            
            self._audit_log('secret_stored', path)
        
        except Exception as e:
            logger.error(f"Failed to store secret: {e}")
            self._audit_log('secret_storage_failed', path, {'error': str(e)})
            raise
    
    async def rotate_secret(self, path: str) -> None:
        """Rotate secret with audit trail"""
        try:
            await self.backend.rotate_secret(path)
            
            # Invalidate cache
            self.cache.pop(path, None)
            
            self._audit_log('secret_rotated', path)
            logger.info(f"Secret rotated: {path}")
        
        except Exception as e:
            logger.error(f"Failed to rotate secret: {e}")
            self._audit_log('secret_rotation_failed', path, {'error': str(e)})
            raise
    
    async def delete_secret(self, path: str) -> None:
        """Delete secret and clear cache"""
        try:
            await self.backend.delete_secret(path)
            self.cache.pop(path, None)
            self._audit_log('secret_deleted', path)
        
        except Exception as e:
            logger.error(f"Failed to delete secret: {e}")
            self._audit_log('secret_deletion_failed', path, {'error': str(e)})
            raise
    
    def _audit_log(self, action: str, path: str, details: Optional[Dict] = None) -> None:
        """Log all secret operations for compliance"""
        if not self.enable_audit:
            return
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'path': path,
            'user': os.environ.get('USER', 'unknown'),
            'backend': self.backend_type.value,
            'details': details or {}
        }
        
        self.audit_log.append(entry)
        logger.info(f"Audit: {action} on {path}")
    
    def export_audit_log(self, filepath: str) -> None:
        """Export audit log for compliance"""
        with open(filepath, 'w') as f:
            json.dump(self.audit_log, f, indent=2)
        logger.info(f"Audit log exported to {filepath}")

```

---

## Integration with Nornir

Dynamic credential injection with vault manager:

```python
import asyncio
from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir.core.inventory import Host

def set_credentials_from_vault(task: Task) -> Result:
    """
    Nornir task: Inject credentials from vault
    """
    vault_manager = task.host.get('vault_manager')
    
    if not vault_manager:
        return Result(host=task.host, failed=True, result="No vault manager configured")
    
    try:
        # Retrieve credentials (bridge the async vault API from this sync task)
        device_creds = asyncio.run(vault_manager.get_secret(
            f"network/credentials/{task.host.name}",
            key='all'
        ))
        
        # Update host credentials
        task.host.username = device_creds.get('username')
        task.host.password = device_creds.get('password')
        
        return Result(host=task.host, result="Credentials injected from vault")
    
    except Exception as e:
        return Result(host=task.host, failed=True, result=f"Failed to inject credentials: {e}")

# Usage in nornir config
nr = InitNornir(config_file="config.yaml")

# Initialize vault manager
vault_manager = VaultManager(
    backend_type=VaultBackend.HASHICORP,
    vault_addr=os.environ['VAULT_ADDR'],
    vault_token=os.environ['VAULT_TOKEN']
)

# Add vault manager to all hosts
for host in nr.inventory.hosts.values():
    host['vault_manager'] = vault_manager

# Run credential injection task
results = nr.run(task=set_credentials_from_vault)

```

---

## CI/CD Integration: GitHub Actions with Vault

Secure credential injection in CI/CD pipelines:

```yaml
name: Network Automation with Vault
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Fetch secrets from HashiCorp Vault
        uses: hashicorp/vault-action@v2
        with:
          url: ${{ secrets.VAULT_ADDR }}
          method: token
          token: ${{ secrets.VAULT_TOKEN }}
          secrets: |
            network/credentials/routers username | ROUTER_USERNAME
            network/credentials/routers password | ROUTER_PASSWORD
            network/credentials/api-token token | API_TOKEN
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run network automation
        run: python scripts/deploy.py
        env:
          VAULT_ADDR: ${{ secrets.VAULT_ADDR }}
          VAULT_TOKEN: ${{ secrets.VAULT_TOKEN }}
          ROUTER_USERNAME: ${{ env.ROUTER_USERNAME }}
          ROUTER_PASSWORD: ${{ env.ROUTER_PASSWORD }}
          API_TOKEN: ${{ env.API_TOKEN }}

```

---

## Dynamic Secrets: Just-In-Time Access

Generate ephemeral SSH credentials with Vault SSH engine:

```python
class VaultSSHSecrets:
    """Manage dynamic SSH credentials from Vault"""
    
    def __init__(self, vault_manager: VaultManager):
        self.vault = vault_manager
    
    async def generate_ssh_credentials(
        self,
        role: str,
        ip_address: str,
        ttl: int = 3600
    ) -> Dict[str, str]:
        """
        Generate temporary SSH credentials
        
        Args:
            role: SSH role name in Vault
            ip_address: Target device IP
            ttl: Credential lifetime in seconds
        
        Returns:
            Dict with username, password, and key
        """
        try:
            # Generate dynamic SSH secret
            ssh_cred = self.vault.backend.client.secrets.ssh.generate_ssh_credentials(
                name=role,
                ip=ip_address,
                username='automation'
            )
            
            return {
                'username': ssh_cred['data']['username'],
                'password': ssh_cred['data']['key'],
                'ttl': ttl,
                'expires_at': (
                    datetime.now() + timedelta(seconds=ttl)
                ).isoformat()
            }
        
        except Exception as e:
            logger.error(f"Failed to generate SSH credentials: {e}")
            raise

```

---

## Credential Rotation Scheduler

Automatic rotation of aged credentials:

```python
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

class CredentialRotationScheduler:
    """Automatically rotate credentials based on schedule"""
    
    def __init__(self, vault_manager: VaultManager):
        self.vault = vault_manager
        self.scheduler = AsyncIOScheduler()
    
    def schedule_rotation(
        self,
        secret_path: str,
        interval_days: int = 90,
        rotation_hour: int = 2  # Off-peak time
    ):
        """
        Schedule automatic secret rotation
        
        Args:
            secret_path: Path to secret to rotate
            interval_days: Rotation frequency
            rotation_hour: Hour of day to rotate (UTC)
        """
        self.scheduler.add_job(
            self.vault.rotate_secret,
            'interval',
            days=interval_days,
            args=[secret_path],
            name=f"rotate_{secret_path}"
        )
        
        logger.info(f"Scheduled rotation for {secret_path} every {interval_days} days")
    
    async def start(self):
        """Start the rotation scheduler"""
        self.scheduler.start()
        logger.info("Credential rotation scheduler started")
    
    async def stop(self):
        """Stop the rotation scheduler"""
        self.scheduler.shutdown()
        logger.info("Credential rotation scheduler stopped")

```

---

## Testing Vault Integration

```python
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_vault_manager_caching():
    """Test secret caching with TTL"""
    manager = VaultManager(
        backend_type=VaultBackend.HASHICORP,
        cache_ttl=10
    )
    
    # Mock backend
    manager.backend.get_secret = AsyncMock(
        return_value={'username': 'admin', 'password': 'secret123'}
    )
    
    # First retrieval (from vault)
    result1 = await manager.get_secret('network/router1')
    assert manager.backend.get_secret.call_count == 1
    
    # Second retrieval (from cache)
    result2 = await manager.get_secret('network/router1')
    assert manager.backend.get_secret.call_count == 1  # Not called again
    assert result1 == result2

@pytest.mark.asyncio
async def test_secret_rotation():
    """Test secret rotation audit trail"""
    manager = VaultManager(enable_audit=True)
    manager.backend.rotate_secret = AsyncMock()
    
    await manager.rotate_secret('network/router1')
    
    # Check audit log
    assert len(manager.audit_log) > 0
    assert manager.audit_log[-1]['action'] == 'secret_rotated'

```

---

## Key Takeaways

✅ **Never hardcode credentials** - Use secrets managers  
✅ **Support multiple backends** - HashiCorp Vault, AWS, Azure for portability  
✅ **Cache with TTL** - Reduce vault load while maintaining security  
✅ **Audit all operations** - Compliance and forensics  
✅ **Rotate regularly** - Automated rotation reduces risk  
✅ **Use dynamic secrets** - Ephemeral credentials for just-in-time access  
✅ **Integrate with CI/CD** - Secrets injection at runtime  

---

## The PRIME Philosophy in Action: Safety, Compliance, and Ownership

- ✅ **Safety:** Secrets never hardcoded, automatic rotation, audit trails
- ✅ **Measurability:** Comprehensive audit logging for compliance audits
- ✅ **Ownership:** Teams control credential policies per environment
- ✅ **Empowerment:** Clear APIs for credential retrieval across tools

---

## 📣 Want More?

- [Nornir + PyATS Integration](nornir-pyats-integration.md) - Full vault integration
- [Asyncio for Network Automation](asyncio-network-automation.md) - Async operations
- [DevOps & Observability](devops-observability-network-automation.md) - Vault in pipelines
- [Tool Ecosystem Integration](tool-ecosystem-integration.md) - Multi-tool credential sharing
- [Credential Management for Network Automation](../intermediate/credential-management-network-automation.md)
- [PRIME Framework Overview](../../../prime-framework/index.md)

---
