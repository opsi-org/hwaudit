
from opsicommon.logging import logger
from opsicommon.objects import AuditHardwareOnHost

from OPSI.System import auditHardware

from hwaudit import __version__


def get_hwaudit(config: dict, host_id: str) -> list[AuditHardwareOnHost]:
	logger.notice("Running hardware inventory")
	return auditHardware(config=config, hostId=host_id)
