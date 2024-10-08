VALUE_MAPPING = {
	"Win32_Processor.Architecture": {
		"0": "x86",
		"1": "MIPS",
		"2": "Alpha",
		"3": "PowerPC",
		"6": "Intel Itanium Processor Family (IPF)",
		"9": "x64",
	},
	"Win32_Processor.Family": {
		"1": "Other",
		"2": "Unknown",
		"3": "8086",
		"4": "80286",
		"5": "Intel386™ Processor",
		"6": "Intel486™ Processor",
		"7": "8087",
		"8": "80287",
		"9": "80387",
		"10": "80487",
		"11": "Pentium Brand",
		"12": "Pentium Pro",
		"13": "Pentium II",
		"14": "Pentium Processor with MMX™ Technology",
		"15": "Celeron™",
		"16": "Pentium II Xeon™",
		"17": "Pentium III",
		"18": "M1 Family",
		"19": "M2 Family",
		"24": "AMD Duron™ Processor Family",
		"25": "K5 Family",
		"26": "K6 Family",
		"27": "K6-2",
		"28": "K6-3",
		"29": "AMD Athlon™ Processor Family",
		"30": "AMD2900 Family",
		"31": "K6-2+",
		"32": "Power PC Family",
		"33": "Power PC 601",
		"34": "Power PC 603",
		"35": "Power PC 603+",
		"36": "Power PC 604",
		"37": "Power PC 620",
		"38": "Power PC X704",
		"39": "Power PC 750",
		"48": "Alpha Family",
		"49": "Alpha 21064",
		"50": "Alpha 21066",
		"51": "Alpha 21164",
		"52": "Alpha 21164PC",
		"53": "Alpha 21164a",
		"54": "Alpha 21264",
		"55": "Alpha 21364",
		"64": "MIPS Family",
		"65": "MIPS R4000",
		"66": "MIPS R4200",
		"67": "MIPS R4400",
		"68": "MIPS R4600",
		"69": "MIPS R10000",
		"80": "SPARC Family",
		"81": "SuperSPARC",
		"82": "microSPARC II",
		"83": "microSPARC IIep",
		"84": "UltraSPARC",
		"85": "UltraSPARC II",
		"86": "UltraSPARC IIi",
		"87": "UltraSPARC III",
		"88": "UltraSPARC IIIi",
		"96": "68040",
		"97": "68xxx Family",
		"98": "68000",
		"99": "68010",
		"100": "68020",
		"101": "68030",
		"112": "Hobbit Family",
		"120": "Crusoe™ TM5000 Family",
		"121": "Crusoe™ TM3000 Family",
		"122": "Efficeon™ TM8000 Family",
		"128": "Weitek",
		"130": "Itanium™ Processor",
		"131": "AMD Athlon™ 64 Processor Famiily",
		"132": "AMD Opteron™ Processor Family",
		"144": "PA-RISC Family",
		"145": "PA-RISC 8500",
		"146": "PA-RISC 8000",
		"147": "PA-RISC 7300LC",
		"148": "PA-RISC 7200",
		"149": "PA-RISC 7100LC",
		"150": "PA-RISC 7100",
		"160": "V30 Family",
		"176": "Pentium III Xeon™ Processor",
		"177": "Pentium III Processor with Intel SpeedStep™ Technology",
		"178": "Pentium 4",
		"179": "Intel Xeon™",
		"180": "AS400 Family",
		"181": "Intel Xeon™ Processor MP",
		"182": "AMD Athlon™ XP Family",
		"183": "AMD Athlon™ MP Family",
		"184": "Intel Itanium 2",
		"185": "Intel Pentium M Processor",
		"190": "K7",
		"200": "IBM390 Family",
		"201": "G4",
		"202": "G5",
		"203": "G6",
		"204": "z/Architecture Base",
		"250": "i860",
		"251": "i960",
		"260": "SH-3",
		"261": "SH-4",
		"280": "ARM",
		"281": "StrongARM",
		"300": "6x86",
		"301": "MediaGX",
		"302": "MII",
		"320": "WinChip",
		"350": "DSP",
		"500": "Video Processor",
	},
	"Win32_SystemSlot.CurrentUsage": {"0": "Reserviert", "1": "Andere", "2": "Unbekannt", "3": "Verfügbar", "4": "Wird verwendet"},
	"Win32_SystemSlot.MaxDataWidth": {"0": 8, "1": 16, "2": 32, "3": 64, "4": 128},
	"Win32_PhysicalMemory.FormFactor": {
		"0": "Unknown",
		"1": "Other",
		"2": "SIP",
		"3": "DIP",
		"4": "ZIP",
		"5": "SOJ",
		"6": "Proprietary",
		"7": "SIMM",
		"8": "DIMM",
		"9": "TSOP",
		"10": "PGA",
		"11": "RIMM",
		"12": "SODIMM",
		"13": "SRIMM",
		"14": "SMD",
		"15": "SSMP",
		"16": "QFP",
		"17": "TQFP",
		"18": "SOIC",
		"19": "LCC",
		"20": "PLCC",
		"21": "BGA",
		"22": "FPBGA",
		"23": "LGA",
	},
	"Win32_PhysicalMemory.MemoryType": {
		"0": "Unknown",
		"1": "Other",
		"2": "DRAM",
		"3": "Synchronous DRAM",
		"4": "Cache DRAM",
		"5": "EDO",
		"6": "EDRAM",
		"7": "VRAM",
		"8": "SRAM",
		"9": "RAM",
		"10": "ROM",
		"11": "Flash",
		"12": "EEPROM",
		"13": "FEPROM",
		"14": "EPROM",
		"15": "CDRAM",
		"16": "3DRAM",
		"17": "SDRAM",
		"18": "SGRAM",
		"19": "RDRAM",
		"20": "DDR",
	},
	"Win32_PhysicalMemoryArray.Location": {
		"0": "Reserved",
		"1": "Other",
		"2": "Unknown",
		"3": "System board or motherboard",
		"4": "ISA add-on card",
		"5": "EISA add-on card",
		"6": "PCI add-on card",
		"7": "MCA add-on card",
		"8": "PCMCIA add-on card",
		"9": "Proprietary add-on card",
		"10": "NuBus",
		"11": "PC-98/C20 add-on card",
		"12": "PC-98/C24 add-on card",
		"13": "PC-98/E add-on card",
		"14": "PC-98/Local bus add-on card",
	},
	"Win32_PhysicalMemoryArray.Use": {
		"0": "Reserved",
		"1": "Other",
		"2": "Unknown",
		"3": "System memory",
		"4": "Video memory",
		"5": "Flash memory",
		"6": "Nonvolatile RAM",
		"7": "Cache memory",
	},
	"Win32_CacheMemory.Level": {"1": "Other", "2": "Unknown", "3": "Primary", "4": "Secondary", "5": "Tertiary"},
	"Win32_CacheMemory.Location": {"0": "Internal", "1": "External", "2": "Reserved", "3": "Unknown"},
	"Win32_PortConnector.ConnectorType": {
		"0": "Unknown",
		"1": "Other",
		"2": "Male",
		"3": "Female",
		"4": "Shielded",
		"5": "Unshielded",
		"6": "SCSI (A) High-Density (50 pins)",
		"7": "SCSI (A) Low-Density (50 pins)",
		"8": "SCSI (P) High-Density (68 pins)",
		"9": "SCSI SCA-I (80 pins)",
		"10": "SCSI SCA-II (80 pins)",
		"11": "SCSI Fibre Channel (DB-9, Copper)",
		"12": "SCSI Fibre Channel (Fibre)",
		"13": "SCSI Fibre Channel SCA-II (40 pins)",
		"14": "SCSI Fibre Channel SCA-II (20 pins)",
		"15": "SCSI Fibre Channel BNC",
		"16": "ATA 3-1/2 Inch (40 pins)",
		"17": "ATA 2-1/2 Inch (44 pins)",
		"18": "ATA-2",
		"19": "ATA-3",
		"20": "ATA/66",
		"21": "DB-9",
		"22": "DB-15",
		"23": "DB-25",
		"24": "DB-36",
		"25": "RS-232C",
		"26": "RS-422",
		"27": "RS-423",
		"28": "RS-485",
		"29": "RS-449",
		"30": "V.35",
		"31": "X.21",
		"32": "IEEE-488",
		"33": "AUI",
		"34": "UTP Category 3",
		"35": "UTP Category 4",
		"36": "UTP Category 5",
		"37": "BNC",
		"38": "RJ11",
		"39": "RJ45",
		"40": "Fiber MIC",
		"41": "Apple AUI",
		"42": "Apple GeoPort",
		"43": "PCI",
		"44": "ISA",
		"45": "EISA",
		"46": "VESA",
		"47": "PCMCIA",
		"48": "PCMCIA Type I",
		"49": "PCMCIA Type II",
		"50": "PCMCIA Type III",
		"51": "ZV Port",
		"52": "CardBus",
		"53": "USB",
		"54": "IEEE 1394",
		"55": "HIPPI",
		"56": "HSSDC (6 pins)",
		"57": "GBIC",
		"58": "DIN",
		"59": "Mini-DIN",
		"60": "Micro-DIN",
		"61": "PS/2",
		"62": "Infrared",
		"63": "HP-HIL",
		"64": "Access.bus",
		"65": "NuBus",
		"66": "Centronics",
		"67": "Mini-Centronics",
		"68": "Mini-Centronics Type-14",
		"69": "Mini-Centronics Type-20",
		"70": "Mini-Centronics Type-26",
		"71": "Bus Mouse",
		"72": "ADB",
		"73": "AGP",
		"74": "VME Bus",
		"75": "VME64",
		"76": "Proprietary",
		"77": "Proprietary Processor Card Slot",
		"78": "Proprietary Memory Card Slot",
		"79": "Proprietary I/O Riser Slot",
		"80": "PCI-66MHZ",
		"81": "AGP2X",
		"82": "AGP4X",
		"83": "PC-98",
		"84": "PC-98-Hireso",
		"85": "PC-H98",
		"86": "PC-98Note",
		"87": "PC-98Full",
		"88": "SSA SCSI",
		"89": "Circular",
		"90": "On Board IDE Connector",
		"91": "On Board Floppy Connector",
		"92": "9 Pin Dual Inline",
		"93": "25 Pin Dual Inline",
		"94": "50 Pin Dual Inline",
		"95": "68 Pin Dual Inline",
		"96": "On Board Sound Connector",
		"97": "Mini-Jack",
		"98": "PCI-X",
		"99": "Sbus IEEE 1396-1993 32 Bit",
		"100": "Sbus IEEE 1396-1993 64 Bit",
		"101": "MCA",
		"102": "GIO",
		"103": "XIO",
		"104": "HIO",
		"105": "NGIO",
		"106": "PMC",
		"107": "MTRJ",
		"108": "VF-45",
		"109": "Future I/O",
		"110": "SC",
		"111": "SG",
		"112": "Electrical",
		"113": "Optical",
		"114": "Ribbon",
		"115": "GLM",
		"116": "1x9",
		"117": "Mini SG",
		"118": "LC",
		"119": "HSSC",
		"120": "VHDCI Shielded (68 pins)",
		"121": "InfiniBand",
	},
	"Win32_NetworkAdapter.NetConnectionStatus": {
		"0": "Disconnected",
		"1": "Connecting",
		"2": "Connected",
		"3": "Disconnecting",
		"4": "Hardware not present",
		"5": "Hardware disabled",
		"6": "Hardware malfunction",
		"7": "Media disconnected",
		"8": "Authenticating",
		"9": "Authentication succeeded",
		"10": "Authentication failed",
		"11": "Invalid address",
		"12": "Credentials required",
	},
	"Win32_NetworkAdapter.AdapterTypeID": {
		"0": "Ethernet 802.3",
		"1": "Token Ring 802.5",
		"2": "Fiber Distributed Data Interface (FDDI)",
		"3": "Wide Area Network (WAN)",
		"4": "LocalTalk",
		"5": "Ethernet using DIX header format",
		"6": "ARCNET",
		"7": "ARCNET (878.2)",
		"8": "ATM",
		"9": "Wireless",
		"10": "Infrared Wireless",
		"11": "Bpc",
		"12": "CoWan",
		"13": "1394",
	},
	"Win32_Printer.Capabilities": {
		"0": "Unknown",
		"1": "Other",
		"2": "Color Printing",
		"3": "Duplex Printing",
		"4": "Copies",
		"5": "Collation",
		"6": "Stapling",
		"7": "Transparency Printing",
		"8": "Punch",
		"9": "Cover",
		"10": "Bind",
		"11": "Black and White Printing",
		"12": "One-Sided",
		"13": "Two-Sided Long Edge",
		"14": "Two-Sided Short Edge",
		"15": "Portrait",
		"16": "Landscape",
		"17": "Reverse Portrait",
		"18": "Reverse Landscape",
		"19": "Quality High",
		"20": "Quality Normal",
		"21": "Quality Low",
	},
	"Win32_Printer.PaperSizesSupported": {
		"0": "Unknown",
		"1": "Other",
		"2": "A",
		"3": "B",
		"4": "C",
		"5": "D",
		"6": "E",
		"7": "Letter",
		"8": "Legal",
		"9": "NA-10x13-Envelpe",
		"10": "NA-9x12-Envelope",
		"11": "NA-Number-10-Envelope",
		"12": "NA-7x9-Envelope",
		"13": "NA-9x11-Envelope",
		"14": "NA-10x14-Envelope",
		"15": "NA-Number-9-Envelope",
		"16": "NA-6x9-Envelope",
		"17": "NA-10x15-Envelope",
		"18": "A0",
		"19": "A1",
		"20": "A2",
		"21": "A3",
		"22": "A4",
		"23": "A5",
		"24": "A6",
		"25": "A7",
		"26": "A8",
		"27": "A9A10",
		"28": "B0",
		"29": "B1",
		"30": "B2",
		"31": "B3",
		"32": "B4",
		"33": "B5",
		"34": "B6",
		"35": "B7",
		"36": "B8",
		"37": "B9",
		"38": "B10",
		"39": "C0",
		"40": "C1",
		"41": "C2",
		"42": "C3",
		"43": "C4",
		"44": "C5",
		"45": "C6",
		"46": "C7",
		"47": "C8",
		"48": "ISO-Designated",
		"49": "JIS B0",
		"50": "JIS B1",
		"51": "JIS B2",
		"52": "JIS B3",
		"53": "JIS B4",
		"54": "JIS B5",
		"55": "JIS B6",
		"56": "JIS B7",
		"57": "JIS B8",
		"58": "JIS B9",
		"59": "JIS B10",
	},
	"Win32_SystemEnclosure.ChassisTypes": {
		"1": "Other",
		"2": "Unknown",
		"3": "Desktop",
		"4": "Low Profile Desktop",
		"5": "Pizza Box",
		"6": "Mini Tower",
		"7": "Tower",
		"8": "Portable",
		"9": "Laptop",
		"10": "Notebook",
		"11": "Hand Held",
		"12": "Docking Station",
		"13": "All in One",
		"14": "Sub Notebook",
		"15": "Space-Saving",
		"16": "Lunch Box",
		"17": "Main System Chassis",
		"18": "Expansion Chassis",
		"19": "SubChassis",
		"20": "Bus Expansion Chassis",
		"21": "Peripheral Chassis",
		"22": "Storage Chassis",
		"23": "Rack Mount Chassis",
		"24": "Sealed-Case PC",
		"25": "Multi-system chassis",
		"26": "Compact PCI",
		"27": "Advanced TCA",
		"28": "Blade",
		"29": "Blade Enclosure",
		"30": "Tablet",
		"31": "Convertible",
		"32": "Detachable",
		"33": "IoT Gateway",
		"34": "Embedded PC",
		"35": "Mini PC",
		"36": "Stick PC",
	},
}
