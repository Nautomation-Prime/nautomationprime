---
title: "Tool Ecosystem Integration for Network Automation: Netbox, ServiceNow, DNA Center, and More"
description: Integrate your automation with industry tools for inventory, ITSM, and intent-based networking.
tags:
  - Expert
  - Tool Integration
  - Netbox
  - ServiceNow
  - DNA Center
  - Network Automation
  - Tutorial
---

## Tool Ecosystem Integration for Network Automation: Netbox, ServiceNow, DNA Center, and More

> *Published: March 1, 2026*  
> *Author: Nautomation Prime Team*

## Why This Tutorial Exists

Modern network automation doesn't exist in isolation. This comprehensive tutorial shows how to integrate with **industry-standard tools** (Netbox, ServiceNow, Cisco DNA Center, AWX, Splunk) for inventory management, change tracking, intent-based networking, and observability. Aligned with the PRIME Framework for transparency and empowerment.

---

## Prerequisites

- Advanced Python (3.8+)
- Understanding of REST API design and authentication
- Familiarity with ITSM workflows (change management, incident tracking)
- Experience with network source-of-truth concepts (inventory)

---

## Architecture: Multi-Tool Orchestration

```text
Network Automation Orchestration
├── Inventory (NetBox)
│   ├── Device database
│   ├── Relationships
│   └── Custom metadata
├── Change Management (ServiceNow)
│   ├── Change tickets
│   ├── Approval workflows
│   └── Compliance tracking
├── Intent & Provisioning (DNA Center)
│   ├── Network intent
│   ├── Device groups
│   └── Compliance policies
├── Execution (AWX)
│   ├── Playbook orchestration
│   ├── Credential management
│   └── Workflow approvals
└── Observability (Splunk)
    ├── Automation events
    ├── Device state changes
    └── Compliance audit logs
```

---

## Part 1: NetBox Integration - Dynamic Inventory

NetBox as the single source of truth for network inventory:

```python
import pynetbox
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from functools import lru_cache
import asyncio
import httpx

logger = logging.getLogger(__name__)

@dataclass
class NetworkDevice:
    """Normalized device representation"""
    name: str
    site: str
    role: str
    platform: str
    primary_ip: str
    serial_number: str
    asset_tag: str
    device_type: str
    custom_fields: Dict[str, Any]

class NetBoxInventoryManager:
    """
    Advanced NetBox integration with:
    - Pagination handling
    - Caching and refresh
    - Filtering and querying
    - Relationship traversal
    - Bulk operations
    """
    
    def __init__(
        self,
        netbox_url: str,
        netbox_token: str,
        verify_ssl: bool = True,
        cache_ttl: int = 3600
    ):
        self.api = pynetbox.api(netbox_url, token=netbox_token)
        self.api.http_session.verify = verify_ssl
        self.cache_ttl = cache_ttl
        self.cache: Dict[str, Any] = {}
        self.cache_time: Dict[str, float] = {}
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cache entry is still valid"""
        import time
        if key not in self.cache_time:
            return False
        return (time.time() - self.cache_time[key]) < self.cache_ttl
    
    def get_all_devices(
        self,
        site: Optional[str] = None,
        role: Optional[str] = None,
        status: str = "active"
    ) -> List[NetworkDevice]:
        """
        Query all devices with filtering
        
        Args:
            site: Filter by site name
            role: Filter by device role
            status: Device status (active, decommissioning, etc.)
        
        Returns:
            List of NetworkDevice objects
        """
        cache_key = f"devices:{site}:{role}:{status}"
        
        if self._is_cache_valid(cache_key):
            logger.debug(f"Cache hit: {cache_key}")
            return self.cache[cache_key]
        
        try:
            filters = {'status': status}
            if site:
                filters['site'] = site
            if role:
                filters['role'] = role
            
            all_devices = []
            for device in self.api.dcim.devices.filter(**filters):
                try:
                    net_device = NetworkDevice(
                        name=device.name,
                        site=device.site.name if device.site else 'unknown',
                        role=device.device_role.name if device.device_role else 'unknown',
                        platform=device.platform.name if device.platform else 'unknown',
                        primary_ip=str(device.primary_ip) if device.primary_ip else '',
                        serial_number=device.serial_number or '',
                        asset_tag=device.asset_tag or '',
                        device_type=device.device_type.model if device.device_type else 'unknown',
                        custom_fields=device.custom_fields or {}
                    )
                    all_devices.append(net_device)
                
                except Exception as e:
                    logger.warning(f"Failed to parse device {device.name}: {e}")
                    continue
            
            # Cache result
            import time
            self.cache[cache_key] = all_devices
            self.cache_time[cache_key] = time.time()
            
            logger.info(f"Retrieved {len(all_devices)} devices from NetBox")
            return all_devices
        
        except Exception as e:
            logger.error(f"Failed to retrieve devices from NetBox: {e}")
            raise
    
    def get_device_by_name(self, name: str) -> Optional[NetworkDevice]:
        """Retrieve specific device by name"""
        try:
            device = self.api.dcim.devices.get(name=name)
            
            return NetworkDevice(
                name=device.name,
                site=device.site.name if device.site else 'unknown',
                role=device.device_role.name if device.device_role else 'unknown',
                platform=device.platform.name if device.platform else 'unknown',
                primary_ip=str(device.primary_ip) if device.primary_ip else '',
                serial_number=device.serial_number or '',
                asset_tag=device.asset_tag or '',
                device_type=device.device_type.model if device.device_type else 'unknown',
                custom_fields=device.custom_fields or {}
            )
        
        except Exception as e:
            logger.error(f"Device not found: {name}")
            return None
    
    def get_device_interfaces(self, device_name: str) -> List[Dict[str, Any]]:
        """Get all interfaces for a device"""
        try:
            device = self.api.dcim.devices.get(name=device_name)
            
            interfaces = []
            for iface in self.api.dcim.interfaces.filter(device=device.id):
                interfaces.append({
                    'name': iface.name,
                    'type': iface.type.get('value', ''),
                    'mtu': iface.mtu,
                    'enabled': iface.enabled,
                    'description': iface.description,
                    'speed': iface.speed,
                    'duplex': iface.duplex.get('value', '') if iface.duplex else ''
                })
            
            return interfaces
        
        except Exception as e:
            logger.error(f"Failed to retrieve interfaces for {device_name}: {e}")
            return []
    
    def create_device(self, device_data: Dict[str, Any]) -> bool:
        """Create new device in NetBox"""
        try:
            created = self.api.dcim.devices.create(**device_data)
            logger.info(f"Created device in NetBox: {created.name}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to create device: {e}")
            return False
    
    def update_device(self, device_name: str, updates: Dict[str, Any]) -> bool:
        """Update existing device in NetBox"""
        try:
            device = self.api.dcim.devices.get(name=device_name)
            
            for key, value in updates.items():
                setattr(device, key, value)
            
            device.save()
            logger.info(f"Updated device in NetBox: {device_name}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to update device {device_name}: {e}")
            return False
    
    def invalidate_cache(self):
        """Clear all caches to force refresh"""
        self.cache.clear()
        self.cache_time.clear()
        logger.info("NetBox cache invalidated")

```

---

## Part 2: ServiceNow Integration - Change Management

Integrate change tickets with network automation:

```python
import requests
import json
import logging
from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ChangeState(Enum):
    """ServiceNow change states"""
    NEW = "-5"
    IN_PROGRESS = "-4"
    PENDING = "-3"
    COMPLETE = "1"
    CLOSED_SUCCESS = "3"
    CLOSED_FAILED = "7"

class ServiceNowChangeManager:
    """
    Advanced ServiceNow integration with:
    - Change ticket creation and tracking
    - Approval workflow integration
    - Risk assessment automation
    - Audit trail generation
    """
    
    def __init__(self, instance_url: str, username: str, password: str):
        self.instance_url = instance_url
        self.auth = (username, password)
        self.base_url = f"https://{instance_url}/api/now"
    
    def create_change_request(
        self,
        short_description: str,
        description: str,
        change_type: str = "Standard",
        priority: int = 3,
        assignment_group: str = "Network Engineering",
        risk_level: str = "Medium",
        impact: str = "Low to Medium"
    ) -> Optional[str]:
        """
        Create change request in ServiceNow
        
        Args:
            short_description: Brief summary
            description: Detailed change description
            change_type: Standard, Normal, Emergency
            priority: 1-5, where 1 is highest
            assignment_group: Team to assign to
            risk_level: Low, Medium, High, Critical
            impact: Expected impact assessment
        
        Returns:
            Change request number (e.g., CHG0123456)
        """
        try:
            payload = {
                'short_description': short_description,
                'description': description,
                'type': change_type,
                'priority': priority,
                'assignment_group.name': assignment_group,
                'risk_assessment': risk_level,
                'justification': f'Automated network change via Nautomation. Impact: {impact}',
                'cab_required': risk_level in ['High', 'Critical'],
                'needs_monitoring': 'true'
            }
            
            headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
            
            response = requests.post(
                f"{self.base_url}/table/change_request",
                auth=self.auth,
                json=payload,
                headers=headers,
                verify=False
            )
            
            if response.status_code != 201:
                logger.error(f"Failed to create change request: {response.text}")
                return None
            
            data = response.json()
            result = data.get('result', {})
            if isinstance(result, list):
                result = result[0] if result else {}
            change_number = result.get('number')
            
            if not change_number:
                logger.error(f"Change request response did not include a number: {data}")
                return None
            
            logger.info(f"Created change request: {change_number}")
            return change_number
        
        except Exception as e:
            logger.error(f"Exception creating change request: {e}")
            return None
    
    def update_change_status(
        self,
        change_number: str,
        state: ChangeState,
        work_notes: str = ""
    ) -> bool:
        """Update change request status"""
        try:
            change = self.get_change_details(change_number)
            if not change or not change.get('sys_id'):
                logger.error(f"Could not find change request: {change_number}")
                return False
            
            payload = {
                'state': state.value,
                'work_notes': work_notes
            }
            
            headers = {'Content-Type': 'application/json'}
            
            response = requests.patch(
                f"{self.base_url}/table/change_request/{change['sys_id']}",
                auth=self.auth,
                json=payload,
                headers=headers,
                verify=False
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to update change: {response.text}")
                return False
            
            logger.info(f"Updated {change_number} to state {state.name}")
            return True
        
        except Exception as e:
            logger.error(f"Exception updating change status: {e}")
            return False
    
    def add_work_notes(self, change_number: str, notes: str) -> bool:
        """Add work notes to change request"""
        try:
            change = self.get_change_details(change_number)
            if not change or not change.get('sys_id'):
                logger.error(f"Could not find change request: {change_number}")
                return False
            
            payload = {'work_notes': notes}
            
            response = requests.patch(
                f"{self.base_url}/table/change_request/{change['sys_id']}",
                auth=self.auth,
                json=payload,
                verify=False
            )
            
            return response.status_code == 200
        
        except Exception as e:
            logger.error(f"Failed to add work notes: {e}")
            return False
    
    def get_change_details(self, change_number: str) -> Optional[Dict[str, Any]]:
        """Retrieve change details"""
        try:
            response = requests.get(
                f"{self.base_url}/table/change_request?sysparm_query=number={change_number}",
                auth=self.auth,
                verify=False
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            return data['result'][0] if data['result'] else None
        
        except Exception as e:
            logger.error(f"Failed to get change details: {e}")
            return None

```

---

## Part 3: Cisco DNA Center Integration

Intent-based networking and device provisioning:

```python
from dnacentersdk import DNACenterAPI
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class DNACenterIntegration:
    """
    Cisco DNA Center integration with:
    - Intent-based networking
    - Device compliance
    - Template provisioning
    - Assurance monitoring
    """
    
    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        verify: bool = False
    ):
        self.api = DNACenterAPI(
            username=username,
            password=password,
            base_url=f"https://{host}",
            verify=verify
        )
    
    def get_devices(self) -> List[Dict[str, Any]]:
        """Get all network devices from DNA Center"""
        try:
            response = self.api.devices.get_device_list()
            
            devices = []
            for device in response['response']:
                devices.append({
                    'id': device['id'],
                    'hostname': device['hostname'],
                    'type': device['type'],
                    'platform_id': device.get('platformId'),
                    'ip': device.get('managementIpAddress'),
                    'status': device.get('managementStatus')
                })
            
            return devices
        
        except Exception as e:
            logger.error(f"Failed to retrieve devices from DNA Center: {e}")
            return []
    
    def get_device_compliance(self, device_id: str) -> Dict[str, Any]:
        """Check device compliance status"""
        try:
            response = self.api.compliance.get_compliance_status(
                deviceId=device_id
            )
            
            return {
                'device_id': device_id,
                'compliance_status': response.get('complianceStatus'),
                'total_configs': response.get('totalConfigs'),
                'non_compliant_configs': response.get('totalNonCompliantConfigs')
            }
        
        except Exception as e:
            logger.error(f"Failed to get compliance status: {e}")
            return {}
    
    def deploy_template(
        self,
        template_id: str,
        target_device_id: str,
        variables: Dict[str, str]
    ) -> Optional[str]:
        """Deploy configuration template to device"""
        try:
            # Render template with variables
            render_response = self.api.configuration_templates.render_config_template(
                templateId=template_id,
                params=variables
            )
            
            rendered_config = render_response['response']['renderedConfig']
            
            # Deploy to device
            deploy_response = self.api.network_device_config.deploy_device_config(
                deviceId=target_device_id,
                request={
                    'config': rendered_config,
                    'taskId': target_device_id
                }
            )
            
            task_id = deploy_response['response']['taskId']
            logger.info(f"Deployed template to {target_device_id}, task: {task_id}")
            
            return task_id
        
        except Exception as e:
            logger.error(f"Failed to deploy template: {e}")
            return None

```

---

## Part 4: AWX Integration

Centralized playbook execution with Ansible Web X (AWX):

```python
import requests
import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class AWXIntegration:
    """AWX (Ansible Web X) integration for playbook execution"""
    
    def __init__(self, tower_url: str, username: str, password: str):
        self.tower_url = tower_url
        self.auth = (username, password)
        self.headers = {'Content-Type': 'application/json'}
    
    def launch_job_template(
        self,
        template_id: int,
        extra_vars: Dict[str, Any],
        inventory_id: Optional[int] = None
    ) -> Optional[int]:
        """
        Launch Ansible job template
        
        Args:
            template_id: Job template ID in Tower
            extra_vars: Variables to pass to playbook
            inventory_id: Optional override inventory
        
        Returns:
            Job ID
        """
        try:
            payload = {
                'extra_vars': json.dumps(extra_vars)
            }
            
            if inventory_id:
                payload['inventory'] = inventory_id
            
            response = requests.post(
                f"{self.tower_url}/api/v2/job_templates/{template_id}/launch/",
                auth=self.auth,
                json=payload,
                headers=self.headers,
                verify=False
            )
            
            if response.status_code != 201:
                logger.error(f"Failed to launch job: {response.text}")
                return None
            
            job_id = response.json()['job']
            logger.info(f"Launched AWX job: {job_id}")
            
            return job_id
        
        except Exception as e:
            logger.error(f"Exception launching job template: {e}")
            return None
    
    def get_job_status(self, job_id: int) -> Optional[Dict[str, Any]]:
        """Get AWX job execution status"""
        try:
            response = requests.get(
                f"{self.tower_url}/api/v2/jobs/{job_id}/",
                auth=self.auth,
                verify=False
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            return {
                'id': job_id,
                'status': data['status'],
                'started': data['started'],
                'finished': data['finished'],
                'failed': data['failed'],
                'result_stdout': data.get('result_stdout', '')
            }
        
        except Exception as e:
            logger.error(f"Failed to get job status: {e}")
            return None

```

---

## Part 5: Complete End-to-End Orchestration

Orchestrating all systems together:

```python
class NetworkAutomationOrchestrator:
    """
    Complete orchestration engine:
    1. Query NetBox for devices
    2. Create change ticket in ServiceNow
    3. Deploy via AWX
    4. Validate with DNA Center
    5. Log to Splunk
    """
    
    def __init__(
        self,
        netbox: NetBoxInventoryManager,
        snow: ServiceNowChangeManager,
        dnac: DNACenterIntegration,
        awx: AWXIntegration
    ):
        self.netbox = netbox
        self.snow = snow
        self.dnac = dnac
        self.awx = awx
    
    async def automate_network_update(
        self,
        change_description: str,
        site: str,
        playbook_template_id: int,
        **extra_vars
    ) -> Dict[str, Any]:
        """
        Execute complete network automation workflow:
        1. Get devices from NetBox by site
        2. Create change request
        3. Deploy configuration via Ansible
        4. Validate compliance in DNA Center
        5. Update change status
        
        Returns:
            Workflow result with change number and status
        """
        result = {
            'change_number': None,
            'deployment_status': 'pending',
            'validation_status': 'pending',
            'devices_affected': 0,
            'errors': []
        }
        
        try:
            # Step 1: Get devices
            logger.info(f"Step 1: Querying NetBox for site {site}")
            devices = self.netbox.get_all_devices(site=site)
            result['devices_affected'] = len(devices)
            
            if not devices:
                result['errors'].append(f"No devices found in {site}")
                return result
            
            # Step 2: Create change request
            logger.info("Step 2: Creating ServiceNow change request")
            change_id = self.snow.create_change_request(
                short_description=f"Automated update: {change_description}",
                description=f"Site: {site}, Devices: {len(devices)}"
            )
            
            if not change_id:
                result['errors'].append("Failed to create change request")
                return result
            
            result['change_number'] = change_id
            
            # Step 3: Deploy via AWX
            logger.info("Step 3: Deploying configuration via AWX")
            extra_vars['devices'] = [d.name for d in devices]
            extra_vars['change_number'] = change_id
            
            job_id = self.awx.launch_job_template(
                playbook_template_id,
                extra_vars=extra_vars
            )
            
            if not job_id:
                self.snow.update_change_status(
                    change_id,
                    ChangeState.CLOSED_FAILED,
                    work_notes="AWX deployment failed"
                )
                result['errors'].append("Failed to launch Ansible job")
                return result
            
            # Wait for deployment
            await asyncio.sleep(10)  # Simplified, should poll job status
            
            result['deployment_status'] = 'completed'
            
            # Step 4: Validate compliance
            logger.info("Step 4: Validating compliance in DNA Center")
            compliance_issues = []
            
            for device in devices[:5]:  # Check first 5
                # Map device name to DNA Center device
                dna_devices = self.dnac.get_devices()
                dna_device = next(
                    (d for d in dna_devices if d['hostname'] == device.name),
                    None
                )
                
                if dna_device:
                    compliance = self.dnac.get_device_compliance(dna_device['id'])
                    if compliance.get('non_compliant_configs', 0) > 0:
                        compliance_issues.append(device.name)
            
            result['validation_status'] = 'completed'
            
            # Step 5: Update change status
            logger.info("Step 5: Updating ServiceNow change status")
            work_notes = f"Deployment completed on {len(devices)} devices"
            if compliance_issues:
                work_notes += f". Compliance issues found on: {', '.join(compliance_issues)}"
            
            self.snow.update_change_status(
                change_id,
                ChangeState.COMPLETE,
                work_notes=work_notes
            )
            
            logger.info(f"Workflow completed successfully: {change_id}")
            
        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            result['errors'].append(str(e))
            
            if result['change_number']:
                self.snow.update_change_status(
                    result['change_number'],
                    ChangeState.CLOSED_FAILED,
                    work_notes=f"Automation failed: {e}"
                )
        
        return result

```

---

## Testing Multi-Tool Integration

```python
@pytest.mark.asyncio
async def test_orchestrator_workflow():
    """Test complete orchestration workflow"""
    # Mock all integrations
    netbox = MagicMock(spec=NetBoxInventoryManager)
    snow = MagicMock(spec=ServiceNowChangeManager)
    dnac = MagicMock(spec=DNACenterIntegration)
    awx = MagicMock(spec=AWXIntegration)
    
    # Setup mocks
    netbox.get_all_devices.return_value = [
        NetworkDevice(
            name='router1',
            site='site1',
            role='core',
            platform='ios',
            primary_ip='10.0.0.1',
            serial_number='123456',
            asset_tag='ASSET001',
            device_type='Cisco ASR9K',
            custom_fields={}
        )
    ]
    
    snow.create_change_request.return_value = 'CHG0001234'
    awx.launch_job_template.return_value = 12345
    dnac.get_devices.return_value = [{'hostname': 'router1', 'id': 'abc123'}]
    
    # Run workflow
    orchestrator = NetworkAutomationOrchestrator(netbox, snow, dnac, awx)
    result = await orchestrator.automate_network_update(
        change_description='Test update',
        site='site1',
        playbook_template_id=5,
        vlan_id=100
    )
    
    assert result['change_number'] == 'CHG0001234'
    assert result['deployment_status'] == 'completed'
    assert result['devices_affected'] == 1

```

---

## Key Takeaways

✅ **NetBox is your source of truth** - Dynamic inventory eliminates manual management  
✅ **ServiceNow integration enables governance** - Change tickets and audit trails  
✅ **DNA Center provides intent validation** - Compliance and policy enforcement  
✅ **AWX centralizes execution** - Consistent, auditable playbook runs  
✅ **Orchestration ties it all together** - Multi-tool workflows for complex changes  
✅ **Abstractions enable portability** - Swap tools without rewriting code  

---

## The PRIME Philosophy in Action: Transparency, Empowerment, and Ownership

- ✅ **Transparency:** All changes tracked in NetBox and ServiceNow, audit trails in compliance
- ✅ **Empowerment:** Teams use familiar tools (ServiceNow, Ansible) for automation
- ✅ **Ownership:** Clear orchestration enables teams to own specific workflows
- ✅ **Measurability:** Metrics on deployment success, compliance, and time-to-change

---

## 📣 Want More?

- [Nornir + PyATS Integration](nornir-pyats-integration.md) - Underlying automation engine
- [Asyncio for Network Automation](asyncio-network-automation.md) - Async tool integration
- [Secure Credential Vaulting](secure-credential-vaulting.md) - Tool credentials management
- [DevOps & Observability](devops-observability-network-automation.md) - Tool observability
- [Implementation Roadmap (30/60/90 Days)](../../production-grade-network-automation-principles/implementation-roadmap-30-60-90-days.md)
- [PRIME Framework Overview](../../../prime-framework/index.md)

---
