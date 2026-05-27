import json

from opsi.logging import get_logger
from opsi.opsi.service.model.object import AuditHardwareOnHost, serialize
from opsi.opsi.service.model.type import to_host_id
from opsi_legacy.System import hardwarePredefinedInventory
from opsi_legacy.System.Posix import hardwareExtendedInventory, hardwareInventory

logger = get_logger("hwaudit")


def get_hwaudit(config: list[dict[str, str]], host_id: str) -> list[AuditHardwareOnHost]:
	logger.notice("Running hardware inventory")
	host_id = to_host_id(host_id)
	AuditHardwareOnHost.setHardwareConfig(config)
	auditHardwareOnHosts = []

	logger.notice("Fetching basic hardware information")
	info = hardwareInventory(config)

	logger.notice("Fetching extended hardware information")
	info = hardwareExtendedInventory(config, info)

	logger.notice("Fetching predefined hardware information")
	info = hardwarePredefinedInventory(config, info)

	logger.info("Hardware information:\n%s", json.dumps(serialize(info), indent=4))

	for hardwareClass, devices in info.items():
		if hardwareClass == "SCANPROPERTIES":
			continue
		for device in devices:
			data = {"hardwareClass": hardwareClass}
			for attribute, value in device.items():
				data[str(attribute)] = value
			data["hostId"] = host_id
			auditHardwareOnHosts.append(AuditHardwareOnHost.fromHash(data))
	return auditHardwareOnHosts
