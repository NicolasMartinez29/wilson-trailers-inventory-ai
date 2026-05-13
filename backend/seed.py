"""
Seed realistic Wilson Trailer Company inventory data (English).

Wilson Trailer Co. (est. 1883, HQ Sioux City IA) manufactures:
  - Livestock trailers: Silverstar, Ranch Hand
  - Grain/commodity trailers: Pacesetter
  - Flatbeds: Roadbrute
"""
import random
from datetime import datetime, timedelta
from .database import SessionLocal, Base, engine
from . import models

random.seed(42)
Base.metadata.create_all(bind=engine)


PRODUCTS = [
    # === ALUMINUM RAW MATERIAL ===
    ("WT-ALU-001", "Aluminum sheet 5052 4x10 .080 gauge", "Aluminum Raw", None, 312.00, 84, 30, "Yard 1 - Rack A1", "Alcoa Howmet"),
    ("WT-ALU-002", "Aluminum sheet 5052 4x12 .090 gauge", "Aluminum Raw", None, 398.00, 56, 24, "Yard 1 - Rack A1", "Alcoa Howmet"),
    ("WT-ALU-003", "Aluminum sheet 6061 4x10 .125 gauge", "Aluminum Raw", None, 485.00, 22, 16, "Yard 1 - Rack A2", "Alcoa Howmet"),
    ("WT-ALU-004", "Diamond plate aluminum 4x8 .100 gauge", "Aluminum Raw", None, 268.00, 38, 18, "Yard 1 - Rack A2", "Alcoa Howmet"),
    ("WT-ALU-005", "Slat extrusion 1.5\" perforated Silverstar", "Aluminum Extrusion", "Silverstar", 38.50, 420, 120, "Yard 1 - Bin B1", "Alcoa Howmet"),
    ("WT-ALU-006", "Top rail extrusion 6\" anodized", "Aluminum Extrusion", "Silverstar", 92.00, 180, 60, "Yard 1 - Bin B2", "Alcoa Howmet"),
    ("WT-ALU-007", "Bottom rail Z-post extrusion 8\"", "Aluminum Extrusion", "Pacesetter", 124.00, 95, 40, "Yard 1 - Bin B3", "Alcoa Howmet"),
    ("WT-ALU-008", "Aluminum tubing 2x4 .120 wall", "Aluminum Extrusion", None, 56.00, 240, 80, "Yard 1 - Bin B4", "Alcoa Howmet"),
    ("WT-ALU-009", "Aluminum tubing 2x6 .125 wall", "Aluminum Extrusion", "Roadbrute", 78.00, 168, 60, "Yard 1 - Bin B4", "Alcoa Howmet"),
    ("WT-ALU-010", "Extruded HD floor plank 40\" Silverstar", "Aluminum Extrusion", "Silverstar", 285.00, 64, 20, "Yard 1 - Rack A3", "Wilson Mill Sioux City"),

    # === AXLES & SUSPENSION ===
    ("WT-AXL-100", "Axle Hendrickson INTRAAX AAT 25K", "Axles & Suspension", "Pacesetter", 3850.00, 18, 8, "WH-A - Rack 12", "Hendrickson USA"),
    ("WT-AXL-101", "Axle Hendrickson INTRAAX AANT 22.5K", "Axles & Suspension", "Silverstar", 3420.00, 22, 8, "WH-A - Rack 12", "Hendrickson USA"),
    ("WT-AXL-102", "Axle Hendrickson VANTRAAX HKANT 23K", "Axles & Suspension", "Roadbrute", 4180.00, 6, 4, "WH-A - Rack 13", "Hendrickson USA"),
    ("WT-AXL-103", "Axle Meritor TN-4671 22.5K", "Axles & Suspension", "Ranch Hand", 2640.00, 14, 6, "WH-A - Rack 13", "Meritor Inc"),
    ("WT-AXL-104", "Axle Reyco Granning RAR-240", "Axles & Suspension", "Roadbrute", 2980.00, 9, 4, "WH-A - Rack 13", "Reyco Granning"),
    ("WT-SUS-110", "Leaf spring Hutchens H-9700 9-leaf", "Axles & Suspension", "Ranch Hand", 685.00, 38, 14, "WH-A - Rack 7", "Hutchens Industries"),
    ("WT-SUS-111", "Air bag Firestone W01-358-7039", "Axles & Suspension", None, 175.00, 96, 30, "WH-A - Rack 8", "Firestone Industrial"),
    ("WT-SUS-112", "Shock absorber Monroe Gas-Magnum 65", "Axles & Suspension", None, 88.00, 124, 40, "WH-A - Rack 8", "Monroe / Tenneco"),
    ("WT-SUS-113", "U-bolt kit 7/8\" HD suspension", "Axles & Suspension", None, 32.50, 320, 100, "WH-A - Bin 4", "Fastenal"),

    # === WHEELS & TIRES ===
    ("WT-WHL-200", "Tire Michelin XZA2 11R22.5 LRH", "Wheels & Tires", None, 412.00, 64, 24, "WH-B - Bay 1", "Michelin North America"),
    ("WT-WHL-201", "Tire Michelin X One Line 445/50R22.5", "Wheels & Tires", "Roadbrute", 685.00, 28, 12, "WH-B - Bay 1", "Michelin North America"),
    ("WT-WHL-202", "Tire Bridgestone R268 Ecopia 11R22.5", "Wheels & Tires", None, 398.00, 52, 20, "WH-B - Bay 1", "Bridgestone Americas"),
    ("WT-WHL-203", "Tire Bridgestone Greatec R197 445/50R22.5", "Wheels & Tires", None, 720.00, 22, 8, "WH-B - Bay 1", "Bridgestone Americas"),
    ("WT-WHL-204", "Wheel Alcoa Dura-Bright EVO 22.5x8.25", "Wheels & Tires", None, 285.00, 88, 30, "WH-B - Bay 2", "Alcoa Wheels"),
    ("WT-WHL-205", "Wheel Alcoa forged 22.5x9.00", "Wheels & Tires", None, 318.00, 42, 18, "WH-B - Bay 2", "Alcoa Wheels"),
    ("WT-WHL-206", "Wheel Accuride steel 22.5x8.25", "Wheels & Tires", None, 145.00, 36, 16, "WH-B - Bay 2", "Accuride"),
    ("WT-WHL-207", "Lug nut 33mm chrome (set 10)", "Wheels & Tires", None, 48.00, 120, 30, "WH-B - Bin 3", "Spike Lug Nuts"),

    # === BRAKES & ABS ===
    ("WT-BRK-300", "ABS system Bendix EC-80 4S/2M", "Brakes", "Silverstar", 1240.00, 14, 6, "WH-C - Rack 3", "Bendix Commercial"),
    ("WT-BRK-301", "ABS system Wabco TCS II 4S/2M", "Brakes", "Pacesetter", 1180.00, 10, 5, "WH-C - Rack 3", "Wabco / ZF"),
    ("WT-BRK-302", "Brake chamber Haldex GoldSeal 30/30", "Brakes", None, 165.00, 96, 30, "WH-C - Rack 4", "Haldex Group"),
    ("WT-BRK-303", "Brake chamber Haldex 36/36 HD", "Brakes", "Roadbrute", 195.00, 48, 16, "WH-C - Rack 4", "Haldex Group"),
    ("WT-BRK-304", "Brake drum Webb Wheel 16.5x7", "Brakes", None, 215.00, 42, 16, "WH-C - Rack 5", "Webb Wheel"),
    ("WT-BRK-305", "Brake drum Gunite 16.5x8.625 HD", "Brakes", "Roadbrute", 268.00, 24, 10, "WH-C - Rack 5", "Gunite"),
    ("WT-BRK-306", "Brake lining MGM Q-Plus FF", "Brakes", None, 78.00, 168, 50, "WH-C - Rack 6", "MGM Brakes"),
    ("WT-BRK-307", "Brake disc Meritor EX+ 17\"", "Brakes", "Pacesetter", 385.00, 8, 4, "WH-C - Rack 5", "Meritor Inc"),
    ("WT-BRK-308", "Relay valve Bendix R-14", "Brakes", None, 92.00, 34, 12, "WH-C - Bin 9", "Bendix Commercial"),

    # === ELECTRICAL & LIGHTING ===
    ("WT-ELE-400", "LED stop/tail Grote LED44", "Electrical", None, 38.00, 280, 80, "WH-E - Rack 1", "Grote Industries"),
    ("WT-ELE-401", "LED amber marker Truck-Lite Super 44", "Electrical", None, 22.00, 360, 100, "WH-E - Rack 1", "Truck-Lite"),
    ("WT-ELE-402", "LED stop/tail/turn Truck-Lite 60-series", "Electrical", None, 42.00, 184, 60, "WH-E - Rack 1", "Truck-Lite"),
    ("WT-ELE-403", "LED clearance Peterson PM168A", "Electrical", None, 14.50, 420, 120, "WH-E - Rack 1", "Peterson MFG"),
    ("WT-ELE-404", "LED dome interior Optronics", "Electrical", "Silverstar", 28.00, 86, 30, "WH-E - Rack 2", "Optronics"),
    ("WT-ELE-405", "ABS harness Phillips QCMS2 7-way", "Electrical", None, 145.00, 48, 18, "WH-E - Rack 2", "Phillips Industries"),
    ("WT-ELE-406", "Coiled cable Permalogic 12ft", "Electrical", None, 68.00, 92, 24, "WH-E - Rack 2", "Phillips Industries"),
    ("WT-ELE-407", "Receptacle Phillips Sta-Dry", "Electrical", None, 52.00, 78, 24, "WH-E - Bin 3", "Phillips Industries"),
    ("WT-ELE-408", "Main wire harness 50ft 16AWG 7-cond", "Electrical", None, 89.00, 64, 20, "WH-E - Rack 2", "Phillips Industries"),

    # === LIVESTOCK SPECIFIC ===
    ("WT-LIV-500", "Center cattle divider gate Silverstar", "Livestock", "Silverstar", 485.00, 14, 6, "WH-G - Livestock", "Wilson Mill Sioux City"),
    ("WT-LIV-501", "Folding cut gate cattle 48\"", "Livestock", "Silverstar", 320.00, 22, 8, "WH-G - Livestock", "Wilson Mill Sioux City"),
    ("WT-LIV-502", "Folding aluminum loading ramp Ranch Hand", "Livestock", "Ranch Hand", 1240.00, 5, 3, "WH-G - Livestock", "Wilson Mill Sioux City"),
    ("WT-LIV-503", "Cattle cleats non-slip (set 12)", "Livestock", "Silverstar", 145.00, 64, 20, "WH-G - Bin 1", "Roppe"),
    ("WT-LIV-504", "Hog floor matting 4x8 rubber", "Livestock", "Silverstar", 88.00, 38, 16, "WH-G - Bin 2", "Roppe"),
    ("WT-LIV-505", "Jail bar slat partition aluminum", "Livestock", "Silverstar", 92.00, 84, 24, "WH-G - Rack 3", "Wilson Mill Sioux City"),
    ("WT-LIV-506", "Folding belly gate hog deck", "Livestock", "Silverstar", 580.00, 8, 4, "WH-G - Rack 4", "Wilson Mill Sioux City"),
    ("WT-LIV-507", "Drop floor mechanism set Silverstar", "Livestock", "Silverstar", 845.00, 4, 3, "WH-G - Rack 4", "Wilson Mill Sioux City"),

    # === GRAIN SPECIFIC ===
    ("WT-GRN-600", "Aulick hydraulic discharge gate 24\"", "Grain", "Pacesetter", 985.00, 7, 4, "WH-G - Grain", "Aulick Industries"),
    ("WT-GRN-601", "Trap valve Walinga 200-series", "Grain", "Pacesetter", 845.00, 6, 3, "WH-G - Grain", "Walinga"),
    ("WT-GRN-602", "Roll tarp Shur-Co 4500 HD", "Grain", "Pacesetter", 1450.00, 4, 3, "WH-G - Grain", "Shur-Co LLC"),
    ("WT-GRN-603", "Shur-Lok aluminum system 40ft", "Grain", "Pacesetter", 685.00, 9, 4, "WH-G - Grain", "Shur-Co LLC"),
    ("WT-GRN-604", "Sight glass Bee-Lite 4\"", "Grain", "Pacesetter", 65.00, 38, 14, "WH-G - Bin 5", "Bee-Lite"),
    ("WT-GRN-605", "Side ladder aluminum 12-step", "Grain", "Pacesetter", 245.00, 18, 8, "WH-G - Rack 6", "Wilson Mill Sioux City"),
    ("WT-GRN-606", "Hopper ring pneumatic 14\"", "Grain", "Pacesetter", 178.00, 14, 6, "WH-G - Rack 6", "Wilson Mill Sioux City"),
    ("WT-GRN-607", "Grain level indicator ROTO-DRO 360", "Grain", "Pacesetter", 92.00, 22, 10, "WH-G - Bin 7", "Walinga"),

    # === FLATBED / ROADBRUTE ===
    ("WT-FLB-700", "Apitong oak floor plank 1.5\" 48\"", "Floors", "Roadbrute", 145.00, 28, 12, "WH-D - Floors", "Wilson Mill Sioux City"),
    ("WT-FLB-701", "Sliding tandem rail Holland SAF-T-LITE", "Flatbed", "Roadbrute", 985.00, 6, 3, "WH-D - Rack 8", "SAF-Holland"),
    ("WT-FLB-702", "Aluminum stake pocket HD (pair)", "Flatbed", "Roadbrute", 32.00, 168, 50, "WH-D - Bin 10", "Buyers Products"),
    ("WT-FLB-703", "Ratchet winch 4\" deck Kinedyne", "Flatbed", "Roadbrute", 78.00, 96, 30, "WH-D - Rack 9", "Kinedyne"),
    ("WT-FLB-704", "Tie-down D-ring weld-on", "Flatbed", "Roadbrute", 14.50, 280, 80, "WH-D - Bin 10", "Buyers Products"),
    ("WT-FLB-705", "Aluminum headache rack Commander", "Flatbed", "Commander", 685.00, 4, 3, "WH-D - Rack 11", "Wilson Mill Sioux City"),

    # === KING PIN / LANDING GEAR / COUPLINGS ===
    ("WT-CPL-800", "King pin SAF-Holland 2.0\" Class A", "Couplings", None, 285.00, 22, 8, "WH-H - Rack 1", "SAF-Holland"),
    ("WT-CPL-801", "Landing gear Holland Mark V 2-speed", "Couplings", None, 685.00, 12, 6, "WH-H - Rack 1", "SAF-Holland"),
    ("WT-CPL-802", "Hydraulic jack leg Jost A480", "Couplings", None, 545.00, 8, 4, "WH-H - Rack 2", "Jost International"),
    ("WT-CPL-803", "Pintle hook Buyers 50-ton", "Couplings", None, 248.00, 14, 6, "WH-H - Rack 2", "Buyers Products"),
    ("WT-CPL-804", "Glad hand red EM SAF-T", "Couplings", None, 18.00, 240, 60, "WH-H - Bin 3", "Phillips Industries"),
    ("WT-CPL-805", "Glad hand blue SR SAF-T", "Couplings", None, 18.00, 240, 60, "WH-H - Bin 3", "Phillips Industries"),

    # === AIR SYSTEMS ===
    ("WT-AIR-900", "Nylon air hose 1/2\" red DOT (100ft)", "Air Systems", None, 128.00, 24, 10, "WH-C - Rack 8", "Parker Hannifin"),
    ("WT-AIR-901", "Nylon air hose 1/2\" blue DOT (100ft)", "Air Systems", None, 128.00, 24, 10, "WH-C - Rack 8", "Parker Hannifin"),
    ("WT-AIR-902", "Aluminum air tank 2200ci", "Air Systems", None, 245.00, 18, 6, "WH-C - Rack 9", "Haldex Group"),
    ("WT-AIR-903", "Steel air tank 3000ci", "Air Systems", "Roadbrute", 168.00, 16, 8, "WH-C - Rack 9", "Haldex Group"),
    ("WT-AIR-904", "Push-Lok brass fitting 1/2\" (set 25)", "Air Systems", None, 38.00, 84, 24, "WH-C - Bin 10", "Parker Hannifin"),

    # === PAINT & FINISH ===
    ("WT-PNT-A00", "Paint Champion Red Wilson 5gal", "Paint & Finish", None, 285.00, 18, 6, "WH-F - Paint", "Sherwin Williams"),
    ("WT-PNT-A01", "Paint Wilson White 5gal", "Paint & Finish", None, 265.00, 22, 6, "WH-F - Paint", "Sherwin Williams"),
    ("WT-PNT-A02", "Epoxy primer 2K 1gal", "Paint & Finish", None, 78.00, 32, 10, "WH-F - Paint", "PPG Industries"),
    ("WT-PNT-A03", "Polyurethane clearcoat 1gal", "Paint & Finish", None, 92.00, 28, 8, "WH-F - Paint", "PPG Industries"),
    ("WT-PNT-A04", "3M DOT-C2 reflective tape (150ft)", "Paint & Finish", None, 145.00, 42, 12, "WH-F - Rack 1", "3M"),
    ("WT-PNT-A05", "Wilson Trailers logo decal large", "Paint & Finish", None, 38.00, 124, 30, "WH-F - Bin 2", "Wilson Mill Sioux City"),
    ("WT-PNT-A06", "3M VHB double-sided sealant (roll)", "Paint & Finish", None, 68.00, 42, 14, "WH-F - Bin 3", "3M"),

    # === HARDWARE ===
    ("WT-HRD-B00", "Hardware assembly kit Silverstar", "Hardware", "Silverstar", 145.00, 56, 16, "WH-E - Rack 5", "Fastenal"),
    ("WT-HRD-B01", "Hardware assembly kit Pacesetter", "Hardware", "Pacesetter", 168.00, 32, 12, "WH-E - Rack 5", "Fastenal"),
    ("WT-HRD-B02", "Rear door hinge HD stainless", "Hardware", "Silverstar", 92.00, 28, 12, "WH-E - Rack 5", "Wilson Mill Sioux City"),
    ("WT-HRD-B03", "Cam-lock stainless gate latch", "Hardware", "Pacesetter", 165.00, 22, 8, "WH-E - Rack 6", "Buyers Products"),
    ("WT-HRD-B04", "Structural rivet 1/4\" stainless (box 500)", "Hardware", None, 78.00, 96, 30, "WH-E - Bin 7", "Avdel / Stanley"),
    ("WT-HRD-B05", "Aluminum rivet 3/16\" (box 1000)", "Hardware", None, 42.00, 168, 40, "WH-E - Bin 7", "POP / Stanley"),
    ("WT-HRD-B06", "Mud flap reinforced 24x30 Wilson logo", "Hardware", None, 28.50, 280, 60, "WH-E - Bin 8", "Buyers Products"),
    ("WT-HRD-B07", "Mud flap bracket stainless", "Hardware", None, 24.00, 240, 60, "WH-E - Bin 8", "Buyers Products"),
    ("WT-HRD-B08", "ICC rear impact guard DOT-compliant", "Hardware", "Roadbrute", 285.00, 14, 6, "WH-E - Rack 9", "Wilson Mill Sioux City"),
]

VENDORS = [
    "Hendrickson USA", "Meritor Inc", "Bendix Commercial Vehicle",
    "Wabco / ZF", "Alcoa Wheels", "Alcoa Howmet",
    "Michelin North America", "Bridgestone Americas",
    "Hutchens Industries", "Haldex Group", "Phillips Industries",
    "Grote Industries", "Truck-Lite", "Peterson MFG", "Optronics",
    "Sherwin Williams", "PPG Industries", "3M Industrial",
    "Fastenal", "Buyers Products", "Parker Hannifin",
    "Shur-Co LLC", "Aulick Industries", "Walinga Inc",
    "SAF-Holland", "Jost International", "Webb Wheel",
    "Gunite", "MGM Brakes", "Kinedyne",
]

EXPENSE_CATEGORIES = [
    ("Shop payroll - welders", "MIG/TIG welder wages Sioux City plant", 18500, 32000),
    ("Shop payroll - assemblers", "Main line assembly wages", 14200, 26800),
    ("Admin payroll", "Office staff + engineering", 22000, 38000),
    ("Electricity", "MidAmerican Energy - plant load", 4200, 9800),
    ("Natural gas", "Paint booth ovens + heating", 1800, 4400),
    ("Machinery maintenance", "Hydraulic press + brake press service", 450, 2800),
    ("Paint booth maintenance", "Booth service + HEPA filters", 380, 1850),
    ("Fleet fuel", "Internal transfer fleet diesel", 280, 1200),
    ("Internal transport", "Inter-plant freight (Sioux/Yankton/Moberly)", 850, 3400),
    ("Office supplies", "Admin consumables", 120, 580),
    ("Shop consumables", "Cut-off discs, electrodes, abrasives", 420, 2200),
    ("PPE - safety gear", "Welding helmets, gloves, boots, glasses", 285, 1400),
    ("Internet & telecom", "Plant + offices monthly", 380, 720),
    ("Plant + fleet insurance", "Travelers Insurance monthly premium", 4200, 6800),
    ("Training", "AWS D1.2 aluminum certification", 600, 2400),
    ("Marketing", "Digital ads + Mid-America Trucking Show", 900, 4500),
    ("Engineering R&D", "New model design + prototypes", 1800, 7500),
]

PAID_TO_POOL = [
    "MidAmerican Energy", "Black Hills Energy", "CenturyLink Business",
    "Sioux City Auto Parts", "United Rentals", "Office Depot",
    "Wells Fargo Bank", "Travelers Insurance", "ADP Payroll",
    "Northland Welding Supply", "Praxair", "Lincoln Electric",
    "FedEx Freight", "Old Dominion Freight",
    "Mid-America Trucking Show LLC", "Verizon Business",
    "Grainger Industrial Supply", "MSC Direct", "Internal payroll",
]


# Bill-of-Materials by trailer line (quantities per ONE trailer).
BOMS = {
    "Silverstar": [
        ("WT-ALU-002", 8), ("WT-ALU-005", 24), ("WT-ALU-006", 4), ("WT-ALU-010", 6),
        ("WT-AXL-101", 2), ("WT-SUS-111", 4), ("WT-SUS-112", 4), ("WT-SUS-113", 4),
        ("WT-WHL-200", 8), ("WT-WHL-204", 8), ("WT-WHL-207", 1),
        ("WT-BRK-300", 1), ("WT-BRK-302", 4), ("WT-BRK-304", 4),
        ("WT-BRK-306", 4), ("WT-BRK-308", 1),
        ("WT-ELE-400", 4), ("WT-ELE-401", 8), ("WT-ELE-403", 12),
        ("WT-ELE-404", 2), ("WT-ELE-405", 1), ("WT-ELE-406", 1), ("WT-ELE-408", 1),
        ("WT-LIV-500", 1), ("WT-LIV-501", 2), ("WT-LIV-503", 1),
        ("WT-LIV-505", 6), ("WT-LIV-507", 1),
        ("WT-CPL-800", 1), ("WT-CPL-801", 2), ("WT-CPL-804", 1), ("WT-CPL-805", 1),
        ("WT-AIR-900", 1), ("WT-AIR-901", 1), ("WT-AIR-902", 2), ("WT-AIR-904", 1),
        ("WT-PNT-A00", 1), ("WT-PNT-A01", 0.5), ("WT-PNT-A02", 1), ("WT-PNT-A03", 1),
        ("WT-PNT-A04", 1), ("WT-PNT-A05", 2),
        ("WT-HRD-B00", 1), ("WT-HRD-B02", 4), ("WT-HRD-B04", 2),
        ("WT-HRD-B05", 1), ("WT-HRD-B06", 4), ("WT-HRD-B07", 4),
    ],
    "Ranch Hand": [
        ("WT-ALU-001", 6), ("WT-ALU-005", 16), ("WT-ALU-008", 8),
        ("WT-AXL-103", 2), ("WT-SUS-110", 4), ("WT-SUS-113", 4),
        ("WT-WHL-202", 8), ("WT-WHL-206", 8),
        ("WT-BRK-302", 4), ("WT-BRK-304", 4), ("WT-BRK-306", 4),
        ("WT-ELE-400", 4), ("WT-ELE-401", 6), ("WT-ELE-403", 10),
        ("WT-ELE-405", 1), ("WT-ELE-408", 1),
        ("WT-LIV-502", 1), ("WT-LIV-503", 1), ("WT-LIV-505", 4),
        ("WT-CPL-800", 1), ("WT-CPL-801", 2), ("WT-CPL-804", 1), ("WT-CPL-805", 1),
        ("WT-AIR-900", 1), ("WT-AIR-901", 1), ("WT-AIR-902", 1),
        ("WT-PNT-A00", 1), ("WT-PNT-A02", 1), ("WT-PNT-A04", 1), ("WT-PNT-A05", 2),
        ("WT-HRD-B04", 2), ("WT-HRD-B06", 4), ("WT-HRD-B07", 4),
    ],
    "Pacesetter": [
        ("WT-ALU-003", 4), ("WT-ALU-007", 8), ("WT-ALU-008", 12),
        ("WT-AXL-100", 3), ("WT-SUS-111", 6), ("WT-SUS-112", 6),
        ("WT-WHL-200", 12), ("WT-WHL-204", 12),
        ("WT-BRK-301", 1), ("WT-BRK-302", 6), ("WT-BRK-304", 6),
        ("WT-BRK-307", 1), ("WT-BRK-308", 1),
        ("WT-ELE-400", 4), ("WT-ELE-401", 10), ("WT-ELE-403", 14),
        ("WT-ELE-405", 1), ("WT-ELE-408", 1),
        ("WT-GRN-600", 2), ("WT-GRN-601", 1), ("WT-GRN-602", 1),
        ("WT-GRN-603", 1), ("WT-GRN-604", 2), ("WT-GRN-605", 1),
        ("WT-GRN-606", 4), ("WT-GRN-607", 1),
        ("WT-CPL-800", 1), ("WT-CPL-801", 2), ("WT-CPL-804", 1), ("WT-CPL-805", 1),
        ("WT-AIR-900", 1), ("WT-AIR-901", 1), ("WT-AIR-902", 2),
        ("WT-PNT-A00", 2), ("WT-PNT-A01", 1), ("WT-PNT-A02", 1),
        ("WT-PNT-A04", 1), ("WT-PNT-A05", 2),
        ("WT-HRD-B01", 1), ("WT-HRD-B03", 4), ("WT-HRD-B04", 2),
    ],
    "Roadbrute": [
        ("WT-ALU-004", 4), ("WT-ALU-009", 12),
        ("WT-AXL-102", 2), ("WT-SUS-111", 4), ("WT-SUS-113", 4),
        ("WT-WHL-201", 4), ("WT-WHL-205", 4),
        ("WT-BRK-301", 1), ("WT-BRK-303", 4), ("WT-BRK-305", 4),
        ("WT-ELE-400", 4), ("WT-ELE-401", 8), ("WT-ELE-403", 10),
        ("WT-ELE-405", 1), ("WT-ELE-408", 1),
        ("WT-FLB-700", 18), ("WT-FLB-701", 1), ("WT-FLB-702", 8),
        ("WT-FLB-703", 4), ("WT-FLB-704", 12),
        ("WT-CPL-800", 1), ("WT-CPL-801", 2), ("WT-CPL-804", 1), ("WT-CPL-805", 1),
        ("WT-AIR-900", 1), ("WT-AIR-901", 1), ("WT-AIR-903", 2),
        ("WT-PNT-A00", 1), ("WT-PNT-A02", 1), ("WT-PNT-A04", 1), ("WT-PNT-A05", 2),
        ("WT-HRD-B04", 2), ("WT-HRD-B06", 4), ("WT-HRD-B07", 4),
        ("WT-HRD-B08", 1),
    ],
}


def run():
    db = SessionLocal()
    db.query(models.WorkOrder).delete()
    db.query(models.BOMLine).delete()
    db.query(models.StockMovement).delete()
    db.query(models.PurchaseItem).delete()
    db.query(models.Purchase).delete()
    db.query(models.Expense).delete()
    db.query(models.Product).delete()
    db.commit()

    for sku, name, cat, line, cost, stock, mn, loc, sup in PRODUCTS:
        db.add(models.Product(
            sku=sku, name=name, category=cat, trailer_line=line,
            unit_cost=cost, stock=stock, min_stock=mn,
            location=loc, supplier=sup,
        ))
    db.commit()

    products = db.query(models.Product).all()
    by_sku = {p.sku: p for p in products}

    for line, items in BOMS.items():
        for sku, qty in items:
            p = by_sku.get(sku)
            if not p:
                continue
            db.add(models.BOMLine(trailer_line=line, product_id=p.id, quantity=qty))
    db.commit()

    now = datetime.utcnow()

    # Purchases — last 240 days
    for i in range(160):
        day_offset = random.randint(0, 240)
        date = now - timedelta(days=day_offset, hours=random.randint(0, 8))
        po = f"PO-2026-{1000 + i:04d}"
        vendor = random.choice(VENDORS)
        purchase = models.Purchase(
            po_number=po, vendor=vendor, date=date,
            status="received", total=0.0,
            notes=f"Stock replenishment - {vendor}",
        )
        db.add(purchase)
        db.flush()

        chosen = random.sample(products, k=random.randint(2, 6))
        total = 0.0
        for prod in chosen:
            qty = random.randint(8, 80)
            cost = round(prod.unit_cost * random.uniform(0.92, 1.05), 2)
            line_total = round(qty * cost, 2)
            total += line_total
            db.add(models.PurchaseItem(
                purchase_id=purchase.id, product_id=prod.id,
                quantity=qty, unit_cost=cost, line_total=line_total,
            ))
            db.add(models.StockMovement(
                date=date, product_id=prod.id,
                movement_type="IN", quantity=qty,
                reason=f"Purchase {po}", reference=po,
            ))
        purchase.total = round(total, 2)
    db.commit()

    # Expenses
    for _ in range(380):
        day_offset = random.randint(0, 240)
        date = now - timedelta(days=day_offset, hours=random.randint(8, 19))
        cat, desc, lo, hi = random.choice(EXPENSE_CATEGORIES)
        amount = round(random.uniform(lo, hi), 2)
        db.add(models.Expense(
            date=date, category=cat, description=desc,
            amount=amount,
            paid_to=random.choice(PAID_TO_POOL),
        ))
    db.commit()

    # Work orders
    for i in range(30):
        line = random.choice(list(BOMS.keys()))
        qty = random.choice([1, 1, 1, 2])
        day_offset = random.randint(0, 240)
        date = now - timedelta(days=day_offset, hours=random.randint(7, 17))
        wo_num = f"WO-{6000 + i:04d}"

        bom = db.query(models.BOMLine).filter(models.BOMLine.trailer_line == line).all()
        material_cost = 0.0
        for bl in bom:
            consumed = bl.quantity * qty
            material_cost += consumed * bl.product.unit_cost
            db.add(models.StockMovement(
                date=date, product_id=bl.product_id,
                movement_type="OUT",
                quantity=max(1, int(round(consumed))),
                reason=f"Production {line} {wo_num}",
                reference=wo_num,
            ))
        db.add(models.WorkOrder(
            wo_number=wo_num, trailer_line=line, quantity=qty,
            date=date, status="completed",
            material_cost=round(material_cost, 2),
        ))
    db.commit()

    # Rebuild stock from movements
    from sqlalchemy import func
    for p in db.query(models.Product).all():
        initial = next((s for sku, _, _, _, _, s, _, _, _ in PRODUCTS if sku == p.sku), 0)
        ins = db.query(func.coalesce(func.sum(models.StockMovement.quantity), 0)).filter(
            models.StockMovement.product_id == p.id,
            models.StockMovement.movement_type == "IN"
        ).scalar() or 0
        outs = db.query(func.coalesce(func.sum(models.StockMovement.quantity), 0)).filter(
            models.StockMovement.product_id == p.id,
            models.StockMovement.movement_type == "OUT"
        ).scalar() or 0
        p.stock = max(0, initial + int(ins) - int(outs))
    db.commit()

    print("[OK] Seed complete - Wilson Trailer Co.")
    print(f"  Products:    {db.query(models.Product).count()}")
    print(f"  BoM lines:   {db.query(models.BOMLine).count()}")
    print(f"  Purchases:   {db.query(models.Purchase).count()}")
    print(f"  Expenses:    {db.query(models.Expense).count()}")
    print(f"  Work orders: {db.query(models.WorkOrder).count()}")
    print(f"  Movements:   {db.query(models.StockMovement).count()}")


if __name__ == "__main__":
    run()
