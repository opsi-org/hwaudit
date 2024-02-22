from opsicommon.logging import get_logger
from opsicommon.objects import AuditHardwareOnHost

from OPSI.System import auditHardware  # type: ignore[import]

logger = get_logger("hwaudit")


def get_hwaudit(config: dict, host_id: str) -> list[AuditHardwareOnHost]:
	logger.notice("Running hardware inventory")
	return auditHardware(config=config, hostId=host_id)
