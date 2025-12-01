from opsicommon.logging import get_logger
from opsicommon.objects import AuditHardwareOnHost
from opsicommon.types import forceHostId

from OPSI.Util import objectToBeautifiedText
from OPSI.System import hardwarePredefinedInventory  # type: ignore[import]
from OPSI.System.Posix import hardwareInventory, hardwareExtendedInventory  # type: ignore[import]

logger = get_logger("hwaudit")


def get_hwaudit(config: dict, host_id: str) -> list[AuditHardwareOnHost]:
	logger.notice("Running hardware inventory")
	host_id = forceHostId(host_id)
	AuditHardwareOnHost.setHardwareConfig(config)
	auditHardwareOnHosts = []

	logger.notice("Fetching basic hardware information")
	info = hardwareInventory(config)

	logger.notice("Fetching extended hardware information")
	info = hardwareExtendedInventory(config, info)

	logger.notice("Fetching predefined hardware information")
	info = hardwarePredefinedInventory(config, info)

	logger.info("Hardware information:\n%s", objectToBeautifiedText(info))

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
