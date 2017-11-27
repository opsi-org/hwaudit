# -*- coding: utf-8 -*-

# Imports
import getopt
import os
import re
import sys
import wmi

# OPSI imports
from OPSI.Backend.JSONRPC import JSONRPCBackend
from OPSI.Util import objectToBeautifiedText
from OPSI.Object import AuditHardwareOnHost
from OPSI.Types import (
	forceHardwareDeviceId, forceHardwareVendorId, forceInt, forceList,
	forceUnicode, forceUnicodeList)
from OPSI.Logger import Logger, LOG_ERROR, LOG_DEBUG2

__version__ = "4.0.7.1"

logger = Logger()

VALUE_MAPPING = {
	"Win32_Processor.Architecture": {
		"0": u"x86",
		"1": u"MIPS",
		"2": u"Alpha",
		"3": u"PowerPC",
		"6": u"Intel Itanium Processor Family (IPF)",
		"9": u"x64"
	},
	"Win32_Processor.Family": {
		"1": u"Other",
		"2": u"Unknown",
		"3": u"8086",
		"4": u"80286",
		"5": u"Intel386™ Processor",
		"6": u"Intel486™ Processor",
		"7": u"8087",
		"8": u"80287",
		"9": u"80387",
		"10": u"80487",
		"11": u"Pentium Brand",
		"12": u"Pentium Pro",
		"13": u"Pentium II",
		"14": u"Pentium Processor with MMX™ Technology",
		"15": u"Celeron™",
		"16": u"Pentium II Xeon™",
		"17": u"Pentium III",
		"18": u"M1 Family",
		"19": u"M2 Family",
		"24": u"AMD Duron™ Processor Family",
		"25": u"K5 Family",
		"26": u"K6 Family",
		"27": u"K6-2",
		"28": u"K6-3",
		"29": u"AMD Athlon™ Processor Family",
		"30": u"AMD2900 Family",
		"31": u"K6-2+",
		"32": u"Power PC Family",
		"33": u"Power PC 601",
		"34": u"Power PC 603",
		"35": u"Power PC 603+",
		"36": u"Power PC 604",
		"37": u"Power PC 620",
		"38": u"Power PC X704",
		"39": u"Power PC 750",
		"48": u"Alpha Family",
		"49": u"Alpha 21064",
		"50": u"Alpha 21066",
		"51": u"Alpha 21164",
		"52": u"Alpha 21164PC",
		"53": u"Alpha 21164a",
		"54": u"Alpha 21264",
		"55": u"Alpha 21364",
		"64": u"MIPS Family",
		"65": u"MIPS R4000",
		"66": u"MIPS R4200",
		"67": u"MIPS R4400",
		"68": u"MIPS R4600",
		"69": u"MIPS R10000",
		"80": u"SPARC Family",
		"81": u"SuperSPARC",
		"82": u"microSPARC II",
		"83": u"microSPARC IIep",
		"84": u"UltraSPARC",
		"85": u"UltraSPARC II",
		"86": u"UltraSPARC IIi",
		"87": u"UltraSPARC III",
		"88": u"UltraSPARC IIIi",
		"96": u"68040",
		"97": u"68xxx Family",
		"98": u"68000",
		"99": u"68010",
		"100": u"68020",
		"101": u"68030",
		"112": u"Hobbit Family",
		"120": u"Crusoe™ TM5000 Family",
		"121": u"Crusoe™ TM3000 Family",
		"122": u"Efficeon™ TM8000 Family",
		"128": u"Weitek",
		"130": u"Itanium™ Processor",
		"131": u"AMD Athlon™ 64 Processor Famiily",
		"132": u"AMD Opteron™ Processor Family",
		"144": u"PA-RISC Family",
		"145": u"PA-RISC 8500",
		"146": u"PA-RISC 8000",
		"147": u"PA-RISC 7300LC",
		"148": u"PA-RISC 7200",
		"149": u"PA-RISC 7100LC",
		"150": u"PA-RISC 7100",
		"160": u"V30 Family",
		"176": u"Pentium III Xeon™ Processor",
		"177": u"Pentium III Processor with Intel SpeedStep™ Technology",
		"178": u"Pentium 4",
		"179": u"Intel Xeon™",
		"180": u"AS400 Family",
		"181": u"Intel Xeon™ Processor MP",
		"182": u"AMD Athlon™ XP Family",
		"183": u"AMD Athlon™ MP Family",
		"184": u"Intel Itanium 2",
		"185": u"Intel Pentium M Processor",
		"190": u"K7",
		"200": u"IBM390 Family",
		"201": u"G4",
		"202": u"G5",
		"203": u"G6",
		"204": u"z/Architecture Base",
		"250": u"i860",
		"251": u"i960",
		"260": u"SH-3",
		"261": u"SH-4",
		"280": u"ARM",
		"281": u"StrongARM",
		"300": u"6x86",
		"301": u"MediaGX",
		"302": u"MII",
		"320": u"WinChip",
		"350": u"DSP",
		"500": u"Video Processor"
	},
	"Win32_SystemSlot.CurrentUsage": {
		"0": u"Reserviert",
		"1": u"Andere",
		"2": u"Unbekannt",
		"3": u"Verfügbar",
		"4": u"Wird verwendet"
	},
	"Win32_SystemSlot.MaxDataWidth": {
		"0": 8,
		"1": 16,
		"2": 32,
		"3": 64,
		"4": 128
	},
	"Win32_PhysicalMemory.FormFactor": {
		"0": u"Unknown",
		"1": u"Other",
		"2": u"SIP",
		"3": u"DIP",
		"4": u"ZIP",
		"5": u"SOJ",
		"6": u"Proprietary",
		"7": u"SIMM",
		"8": u"DIMM",
		"9": u"TSOP",
		"10": u"PGA",
		"11": u"RIMM",
		"12": u"SODIMM",
		"13": u"SRIMM",
		"14": u"SMD",
		"15": u"SSMP",
		"16": u"QFP",
		"17": u"TQFP",
		"18": u"SOIC",
		"19": u"LCC",
		"20": u"PLCC",
		"21": u"BGA",
		"22": u"FPBGA",
		"23": u"LGA"
	},
	"Win32_PhysicalMemory.MemoryType": {
		"0": u"Unknown",
		"1": u"Other",
		"2": u"DRAM",
		"3": u"Synchronous DRAM",
		"4": u"Cache DRAM",
		"5": u"EDO",
		"6": u"EDRAM",
		"7": u"VRAM",
		"8": u"SRAM",
		"9": u"RAM",
		"10": u"ROM",
		"11": u"Flash",
		"12": u"EEPROM",
		"13": u"FEPROM",
		"14": u"EPROM",
		"15": u"CDRAM",
		"16": u"3DRAM",
		"17": u"SDRAM",
		"18": u"SGRAM",
		"19": u"RDRAM",
		"20": u"DDR"
	},
	"Win32_PhysicalMemoryArray.Location": {
		"0": u"Reserved",
		"1": u"Other",
		"2": u"Unknown",
		"3": u"System board or motherboard",
		"4": u"ISA add-on card",
		"5": u"EISA add-on card",
		"6": u"PCI add-on card",
		"7": u"MCA add-on card",
		"8": u"PCMCIA add-on card",
		"9": u"Proprietary add-on card",
		"10": u"NuBus",
		"11": u"PC-98/C20 add-on card",
		"12": u"PC-98/C24 add-on card",
		"13": u"PC-98/E add-on card",
		"14": u"PC-98/Local bus add-on card"
	},
	"Win32_PhysicalMemoryArray.Use": {
		"0": u"Reserved",
		"1": u"Other",
		"2": u"Unknown",
		"3": u"System memory",
		"4": u"Video memory",
		"5": u"Flash memory",
		"6": u"Nonvolatile RAM",
		"7": u"Cache memory"
	},
	"Win32_CacheMemory.Level": {
		"1": u"Other",
		"2": u"Unknown",
		"3": u"Primary",
		"4": u"Secondary",
		"5": u"Tertiary"
	},
	"Win32_CacheMemory.Location": {
		"0": u"Internal",
		"1": u"External",
		"2": u"Reserved",
		"3": u"Unknown"
	},
	"Win32_PortConnector.ConnectorType": {
		"0": u"Unknown",
		"1": u"Other",
		"2": u"Male",
		"3": u"Female",
		"4": u"Shielded",
		"5": u"Unshielded",
		"6": u"SCSI (A) High-Density (50 pins)",
		"7": u"SCSI (A) Low-Density (50 pins)",
		"8": u"SCSI (P) High-Density (68 pins)",
		"9": u"SCSI SCA-I (80 pins)",
		"10": u"SCSI SCA-II (80 pins)",
		"11": u"SCSI Fibre Channel (DB-9, Copper)",
		"12": u"SCSI Fibre Channel (Fibre)",
		"13": u"SCSI Fibre Channel SCA-II (40 pins)",
		"14": u"SCSI Fibre Channel SCA-II (20 pins)",
		"15": u"SCSI Fibre Channel BNC",
		"16": u"ATA 3-1/2 Inch (40 pins)",
		"17": u"ATA 2-1/2 Inch (44 pins)",
		"18": u"ATA-2",
		"19": u"ATA-3",
		"20": u"ATA/66",
		"21": u"DB-9",
		"22": u"DB-15",
		"23": u"DB-25",
		"24": u"DB-36",
		"25": u"RS-232C",
		"26": u"RS-422",
		"27": u"RS-423",
		"28": u"RS-485",
		"29": u"RS-449",
		"30": u"V.35",
		"31": u"X.21",
		"32": u"IEEE-488",
		"33": u"AUI",
		"34": u"UTP Category 3",
		"35": u"UTP Category 4",
		"36": u"UTP Category 5",
		"37": u"BNC",
		"38": u"RJ11",
		"39": u"RJ45",
		"40": u"Fiber MIC",
		"41": u"Apple AUI",
		"42": u"Apple GeoPort",
		"43": u"PCI",
		"44": u"ISA",
		"45": u"EISA",
		"46": u"VESA",
		"47": u"PCMCIA",
		"48": u"PCMCIA Type I",
		"49": u"PCMCIA Type II",
		"50": u"PCMCIA Type III",
		"51": u"ZV Port",
		"52": u"CardBus",
		"53": u"USB",
		"54": u"IEEE 1394",
		"55": u"HIPPI",
		"56": u"HSSDC (6 pins)",
		"57": u"GBIC",
		"58": u"DIN",
		"59": u"Mini-DIN",
		"60": u"Micro-DIN",
		"61": u"PS/2",
		"62": u"Infrared",
		"63": u"HP-HIL",
		"64": u"Access.bus",
		"65": u"NuBus",
		"66": u"Centronics",
		"67": u"Mini-Centronics",
		"68": u"Mini-Centronics Type-14",
		"69": u"Mini-Centronics Type-20",
		"70": u"Mini-Centronics Type-26",
		"71": u"Bus Mouse",
		"72": u"ADB",
		"73": u"AGP",
		"74": u"VME Bus",
		"75": u"VME64",
		"76": u"Proprietary",
		"77": u"Proprietary Processor Card Slot",
		"78": u"Proprietary Memory Card Slot",
		"79": u"Proprietary I/O Riser Slot",
		"80": u"PCI-66MHZ",
		"81": u"AGP2X",
		"82": u"AGP4X",
		"83": u"PC-98",
		"84": u"PC-98-Hireso",
		"85": u"PC-H98",
		"86": u"PC-98Note",
		"87": u"PC-98Full",
		"88": u"SSA SCSI",
		"89": u"Circular",
		"90": u"On Board IDE Connector",
		"91": u"On Board Floppy Connector",
		"92": u"9 Pin Dual Inline",
		"93": u"25 Pin Dual Inline",
		"94": u"50 Pin Dual Inline",
		"95": u"68 Pin Dual Inline",
		"96": u"On Board Sound Connector",
		"97": u"Mini-Jack",
		"98": u"PCI-X",
		"99": u"Sbus IEEE 1396-1993 32 Bit",
		"100": u"Sbus IEEE 1396-1993 64 Bit",
		"101": u"MCA",
		"102": u"GIO",
		"103": u"XIO",
		"104": u"HIO",
		"105": u"NGIO",
		"106": u"PMC",
		"107": u"MTRJ",
		"108": u"VF-45",
		"109": u"Future I/O",
		"110": u"SC",
		"111": u"SG",
		"112": u"Electrical",
		"113": u"Optical",
		"114": u"Ribbon",
		"115": u"GLM",
		"116": u"1x9",
		"117": u"Mini SG",
		"118": u"LC",
		"119": u"HSSC",
		"120": u"VHDCI Shielded (68 pins)",
		"121": u"InfiniBand"
	},
	"Win32_NetworkAdapter.NetConnectionStatus": {
		"0": u"Disconnected",
		"1": u"Connecting",
		"2": u"Connected",
		"3": u"Disconnecting",
		"4": u"Hardware not present",
		"5": u"Hardware disabled",
		"6": u"Hardware malfunction",
		"7": u"Media disconnected",
		"8": u"Authenticating",
		"9": u"Authentication succeeded",
		"10": u"Authentication failed",
		"11": u"Invalid address",
		"12": u"Credentials required"
	},
	"Win32_NetworkAdapter.AdapterTypeID": {
		"0": u"Ethernet 802.3",
		"1": u"Token Ring 802.5",
		"2": u"Fiber Distributed Data Interface (FDDI)",
		"3": u"Wide Area Network (WAN)",
		"4": u"LocalTalk",
		"5": u"Ethernet using DIX header format",
		"6": u"ARCNET",
		"7": u"ARCNET (878.2)",
		"8": u"ATM",
		"9": u"Wireless",
		"10": u"Infrared Wireless",
		"11": u"Bpc",
		"12": u"CoWan",
		"13": u"1394"
	},
	"Win32_Printer.Capabilities": {
		"0": u"Unknown",
		"1": u"Other",
		"2": u"Color Printing",
		"3": u"Duplex Printing",
		"4": u"Copies",
		"5": u"Collation",
		"6": u"Stapling",
		"7": u"Transparency Printing",
		"8": u"Punch",
		"9": u"Cover",
		"10": u"Bind",
		"11": u"Black and White Printing",
		"12": u"One-Sided",
		"13": u"Two-Sided Long Edge",
		"14": u"Two-Sided Short Edge",
		"15": u"Portrait",
		"16": u"Landscape",
		"17": u"Reverse Portrait",
		"18": u"Reverse Landscape",
		"19": u"Quality High",
		"20": u"Quality Normal",
		"21": u"Quality Low"
	},
	"Win32_Printer.PaperSizesSupported": {
		"0": u"Unknown",
		"1": u"Other",
		"2": u"A",
		"3": u"B",
		"4": u"C",
		"5": u"D",
		"6": u"E",
		"7": u"Letter",
		"8": u"Legal",
		"9": u"NA-10x13-Envelpe",
		"10": u"NA-9x12-Envelope",
		"11": u"NA-Number-10-Envelope",
		"12": u"NA-7x9-Envelope",
		"13": u"NA-9x11-Envelope",
		"14": u"NA-10x14-Envelope",
		"15": u"NA-Number-9-Envelope",
		"16": u"NA-6x9-Envelope",
		"17": u"NA-10x15-Envelope",
		"18": u"A0",
		"19": u"A1",
		"20": u"A2",
		"21": u"A3",
		"22": u"A4",
		"23": u"A5",
		"24": u"A6",
		"25": u"A7",
		"26": u"A8",
		"27": u"A9A10",
		"28": u"B0",
		"29": u"B1",
		"30": u"B2",
		"31": u"B3",
		"32": u"B4",
		"33": u"B5",
		"34": u"B6",
		"35": u"B7",
		"36": u"B8",
		"37": u"B9",
		"38": u"B10",
		"39": u"C0",
		"40": u"C1",
		"41": u"C2",
		"42": u"C3",
		"43": u"C4",
		"44": u"C5",
		"45": u"C6",
		"46": u"C7",
		"47": u"C8",
		"48": u"ISO-Designated",
		"49": u"JIS B0",
		"50": u"JIS B1",
		"51": u"JIS B2",
		"52": u"JIS B3",
		"53": u"JIS B4",
		"54": u"JIS B5",
		"55": u"JIS B6",
		"56": u"JIS B7",
		"57": u"JIS B8",
		"58": u"JIS B9",
		"59": u"JIS B10"
	},
	"Win32_SystemEnclosure.ChassisTypes": {
		"1": u"Other",
		"2": u"Unknown",
		"3": u"Desktop",
		"4": u"Low Profile Desktop",
		"5": u"Pizza Box",
		"6": u"Mini Tower",
		"7": u"Tower",
		"8": u"Portable",
		"9": u"Laptop",
		"10": u"Notebook",
		"11": u"Hand Held",
		"12": u"Docking Station",
		"13": u"All in One",
		"14": u"Sub Notebook",
		"15": u"Space-Saving",
		"16": u"Lunch Box",
		"17": u"Main System Chassis",
		"18": u"Expansion Chassis",
		"19": u"SubChassis",
		"20": u"Bus Expansion Chassis",
		"21": u"Peripheral Chassis",
		"22": u"Storage Chassis",
		"23": u"Rack Mount Chassis",
		"24": u"Sealed-Case PC"
	}
}


def getHardwareInformationFromWMI(conf, win2k=False):
	wmiObj = wmi.WMI()

	opsiValues = {}

	for oneClass in conf:
		if not oneClass.get('Class') or not oneClass['Class'].get('Opsi') or not oneClass['Class'].get('WMI'):
			continue

		opsiName = oneClass['Class']['Opsi']
		wmiQuery = oneClass['Class']['WMI']
		mapClass = ''

		mapSep = '&'
		temp = wmiQuery.split(mapSep)
		if len(temp) == 2:
			wmiQuery = temp[0]
			mapClass = temp[1]

		filter = None
		if win2k:
			idx = wmiQuery.lower().find('where')
			if idx != -1:
				filter = wmiQuery[idx+5:].strip()
				if 'like' not in filter.lower():
					filter = None
				else:
					wmiQuery = wmiQuery[:idx].strip()

		logger.info(u"Querying: %s" % wmiQuery)
		logger.info(u"Filter: %s" % filter)
		objects = []
		try:
			objects = wmiObj.query(wmiQuery)
		except Exception as error:
			logger.error(u"Query failed: %s" % error)
			continue

		# first element? make new array for multiple devices
		if opsiName not in opsiValues:
			opsiValues[opsiName] = []

		for obj in objects:
			wmiClass = obj.ole_object.GetObjectText_().split()[2]
			# Filter objects (Win2k does not support "LIKE")
			if filter:
				try:
					if ' and ' in filter.lower() or ' or ' in filter.lower():
						raise Exception(u"Filter '%s' not supported" % filter)
					at = filter.split()[0]
					op = filter.split()[1]
					va = filter.split()[2][1:-1].replace('\\', '\\\\').replace('%', '.*')
					if op.lower() != 'like':
						raise Exception(u"Operator LIKE expected but '%s' found" % op)
					regex = re.compile(va)
					v = getattr(obj, at)
					logger.info(u"Testing if '%s' matches '%s'" % (v, va))
					if re.search(regex, v):
						logger.info(u"Object matches filter '%s'" % filter)
					else:
						continue
				except Exception as error:
					logger.error("Filter '%s' failed: %s" % (filter, error))
					continue

			obj2 = None
			if mapClass:
				assoc = obj.associators(mapClass)
				if len(assoc) > 0:
					obj2 = assoc[0]

			opsiValues[opsiName].append({})
			for item in oneClass['Values']:
				v = None
				if item.get('WMI'):
					for a in item['WMI'].split('||'):
						a = a.strip()
						c = wmiClass
						if '::' in a:
							(c, a) = a.split('::', 1)
						meth = None
						op = None
						if '.' in a:
							(a, meth) = a.split('.', 1)
						match = re.search('^(\w+)([\*\/\+\-\%]\d.*)$', a)
						if match:
							a = match.group(1)
							op = match.group(2)

						if c == wmiClass and hasattr(obj, a):
							v = getattr(obj, a)
						elif obj2 and hasattr(obj2, a):
							v = getattr(obj2, a)
						else:
							try:
								if obj2:
									logger.warning(u"%s.%s: failed to get attribute '%s' from objects %s" % (opsiName, item['Opsi'], a, [obj.__repr__(), obj2.__repr__()]))
								else:
									logger.warning(u"%s.%s: failed to get attribute '%s' from object '%s'" % (opsiName, item['Opsi'], a, obj.__repr__()))
							except Exception as error:
								logger.error(error)

							continue

						if type(v) is tuple and (len(v) == 1):
							v = v[0]

						if meth and v is not None:
							try:
								v = eval('v.%s' % meth)
							except Exception:
								logger.warning(u"Method '%s' failed on value '%s'" % (meth, v))

						if op and v is not None:
							try:
								v = eval('v%s' % op)
							except Exception:
								logger.warning(u"Operation '%s' failed on value '%s'" % (op, v))

						if item['Opsi'] in ('vendorId', 'subsystemVendorId'):
							try:
								v = forceHardwareVendorId(v)
							except Exception:
								v = None
						elif item['Opsi'] in ('deviceId', 'subsystemDeviceId'):
							try:
								v = forceHardwareDeviceId(v)
							except Exception:
								v = None

						if v is None:
							continue

						if type(v) is str:
							v = forceUnicode(v)
						if type(v) is unicode:
							v = v.strip()

						logger.debug(u"Searching mapping for '%s.%s'" % (c, a))
						if "%s.%s" % (c, a) in VALUE_MAPPING:
							v = forceList(v)
							for i in range(len(v)):
								v[i] = VALUE_MAPPING["%s.%s" % (c, a)].get(str(v[i]), v[i])
							if len(v) == 1:
								v = v[0]
						if type(v) in (list, tuple):
							v = u', '.join(forceUnicodeList(v))

						if item['Type'].startswith('varchar'):
							v = forceUnicode(v)
							maxLen = forceInt(item['Type'].split('(')[1].split(')')[0].strip())
							if len(v) > maxLen:
								logger.warning(u"Truncating value '%s': string is to long" % v)
								v = v[:maxLen]
						if v is not None:
							break
				opsiValues[opsiName][-1][item['Opsi']] = v
			logger.debug(u"Hardware object is now: %s" % opsiValues[opsiName][-1])
			if not opsiValues[opsiName][-1]:
				logger.info(u"Skipping empty object")
				opsiValues[opsiName].pop()

	return opsiValues


def getHardwareInformationFromRegistry(conf, opsiValues={}):
	from OPSI.System.Windows import HKEY_LOCAL_MACHINE, HKEY_CURRENT_USER, getRegistryValue

	regex = re.compile('^\[\s*([^\]]+)\s*\]\s*(\S+.*)\s*$')
	for oneClass in conf:
		if not oneClass.get('Class') or not oneClass['Class'].get('Opsi'):
			continue

		opsiName = oneClass['Class']['Opsi']
		for item in oneClass['Values']:
			registryQuery = item.get('Registry')
			if not registryQuery:
				continue

			logger.info(u"Querying: %s" % registryQuery)
			match = re.search(regex, registryQuery)
			if not match:
				logger.error(u"Bad registry query '%s'" % registryQuery)
				continue

			logger.info(match)
			key = match.group(1)
			if not key.find('\\'):
				logger.error(u"Bad registry query '%s'" % registryQuery)
				continue

			(key, subKey) = key.split('\\', 1)
			valueName = match.group(2)

			if key in ('HKEY_LOCAL_MACHINE', 'HKLM'):
				key = HKEY_LOCAL_MACHINE
			elif key in ('HKEY_CURRENT_USER', 'HKCU'):
				key = HKEY_CURRENT_USER
			else:
				logger.error(u"Unhandled registry key '%s'" % key)
				continue
			try:
				value = getRegistryValue(key, subKey, valueName)
			except Exception as error:
				logger.error(u"Failed to get '%s': %s" % (registryQuery, error))
				continue

			if type(value) is unicode:
				value = value.encode('utf-8')
			if opsiName not in opsiValues:
				opsiValues[opsiName].append({})
			for i in range(len(opsiValues[opsiName])):
				opsiValues[opsiName][i][item['Opsi']] = value
	return opsiValues


def getHardwareInformationFromExecuteCommand(conf, opsiValues={}):
	from OPSI.System.Windows import execute

	regex = re.compile("^#(?P<cmd>.*)#(?P<extend>.*)$")
	for oneClass in conf:
		if not oneClass.get('Class') or not oneClass['Class'].get('Opsi'):
			continue

		opsiName = oneClass['Class']['Opsi']
		for item in oneClass['Values']:
			cmdline = item.get('Cmd')
			if not cmdline:
				continue
			condition = item.get("Condition")
			if condition:
				val = condition.split("=")[0]
				r = condition.split("=")[1]
				if val and r:
					conditionregex = re.compile(r)

					logger.info("Condition found, try to find the Condition")
					for i in range(len(opsiValues[opsiName])):
                                                value = opsiValues[opsiName][i].get(val, "")
                                                if value:
                                                        conditionmatch = re.search(conditionregex, value)
                                                        
                                                                  
					if not conditionmatch:
						continue
			match = re.search(regex, cmdline)
			if not match:
				logger.error(u"Bad Cmd entry '%s'" % cmdline)
				continue
			matchresult = match.groupdict()
			executeCommand = matchresult.get("cmd")
			extend = matchresult.get("extend")

			logger.info(u"Executing: %s" % executeCommand)
			try:
				value = ''
				result = execute(executeCommand)
				if result and extend:
					res = result[0]
					value = eval("res%s" % extend)
			except Exception as error:
				logger.logException(error)
				logger.error("Failed to execute command: '%s' error: '%s'" % (executeCommand, error))
				continue

			if type(value) is unicode:
				value = value.encode('utf-8')
			if opsiName not in opsiValues:
				opsiValues[opsiName].append({})
			for i in range(len(opsiValues[opsiName])):
				opsiValues[opsiName][i][item['Opsi']] = value
	return opsiValues


def usage():
	print "\nUsage: %s -a <address> -u <username> -h <hostid> -p <password>" % os.path.basename(sys.argv[0])
	print "Options:"
	print "      --help           Display this text"
	print "  -u, --username       Username"
	print "  -h, --hostid         Host id"
	print "  -p, --password       Password"
	print "  -a, --address        Address of opsiconfd"
	print ""


def main(argv):
	logger.setLogFile('c:\\tmp\\hwaudit.log')
	logger.setFileLevel(LOG_DEBUG2)

	logger.notice("starting hardware audit")

	win2k = False
	if (sys.getwindowsversion()[0] == 5) and (sys.getwindowsversion()[1] == 0):
		win2k = True

	try:
		(opts, args) = getopt.getopt(
			argv,
			"u:p:a:l:f:h",
			["username=", "password=", "address=", "log-level", "loglevel", "help"]
		)
	except getopt.GetoptError:
		usage()
		sys.exit(1)

	address = u''
	username = u''
	host_id = u''
	password = u''
	loglevel = LOG_ERROR

	for (opt, arg) in opts:
		if opt in ("--help",):
			usage()
			sys.exit(0)
		elif opt in ("-u", "--username"):
			username = arg
		elif opt in ("-h", "--hostid"):
			host_id = arg
		elif opt in ("-p", "--password"):
			password = arg
		elif opt in ("-a", "--address"):
			address = arg
		elif opt in ("-l", "--loglevel"):
			loglevel = int(arg)
		elif opt in ("-f", "--log-file"):
			logger.setLogFile(arg)

	if address.startswith(u"https://"):
		address = address + u"/rpc"

	if not address:
		logger.critical(u"Address not set")
		raise RuntimeError("Address not set")

	if not username:
		if host_id:
			username = host_id
		else:
			logger.critical(u"Host id and username not set")
			raise RuntimeError("Host id and username not set")

	if not host_id:
		if username:
			host_id = username
		else:
			logger.critical(u"Host id and username not set")
			raise RuntimeError("Host id and username not set")

	if not password:
		logger.critical(u"Password not set")
		raise RuntimeError("No password set!")

	logger.setConsoleLevel(loglevel)

	logger.notice(u"Connecting to service at '%s' as '%s'" % (address, username))
	backend = JSONRPCBackend(
		username=username,
		password=password,
		address=address,
		application='opsi hwaudit %s' % __version__
	)
	logger.notice(u"Connected to opsi server")

	logger.notice(u"Fetching opsi hw audit configuration")
	config = backend.auditHardware_getConfig()

	logger.notice(u"Fetching hardware information from WMI")
	values = getHardwareInformationFromWMI(config, win2k)

	logger.notice(u"Fetching hardware information from Registry")
	values = getHardwareInformationFromRegistry(config, values)

	logger.notice(u"Fetching hardware information from Executing Command")
	values = getHardwareInformationFromExecuteCommand(config, values)

	logger.info(u"Hardware information from WMI:\n%s" % objectToBeautifiedText(values))
	logger.notice(u"Sending hardware information to service")
	auditHardwareOnHosts = []
	for (hardwareClass, devices) in values.items():
		if hardwareClass == 'SCANPROPERTIES':
			continue

		for device in devices:
			data = {'hardwareClass': hardwareClass}
			for (attribute, value) in device.items():
				data[str(attribute)] = value
			data['hostId'] = host_id
			auditHardwareOnHosts.append(AuditHardwareOnHost.fromHash(data))

	backend.auditHardwareOnHost_setObsolete(host_id)
	backend.auditHardwareOnHost_updateObjects(auditHardwareOnHosts)

	logger.notice(u"Exiting...")
	backend.backend_exit()


if __name__ == "__main__":
	logger.setConsoleLevel(LOG_ERROR)
	try:
		main(sys.argv[1:])
	except Exception as error:
		logger.logException(error)
		sys.exit(1)
