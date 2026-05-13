"""
Seed realistic Wilson Trailer Company inventory data.

Wilson Trailer Co. (est. 1883, HQ Sioux City IA) manufactures:
  - Livestock trailers: Silverstar, Ranch Hand
  - Grain/commodity trailers: Pacesetter
  - Flatbeds: Roadbrute, Commander

Includes Bill-of-Materials so that producing 1 trailer of a given line
auto-consumes the correct number of part SKUs from inventory.
"""
import random
from datetime import datetime, timedelta
from .database import SessionLocal, Base, engine
from . import models

random.seed(42)
Base.metadata.create_all(bind=engine)


PRODUCTS = [
    # === ALUMINUM RAW MATERIAL ===
    ("WT-ALU-001", "Lámina aluminio 5052 4x10 calibre .080", "Aluminio Bruto", None, 312.00, 84, 30, "Yard 1 — Rack A1", "Alcoa Howmet"),
    ("WT-ALU-002", "Lámina aluminio 5052 4x12 calibre .090", "Aluminio Bruto", None, 398.00, 56, 24, "Yard 1 — Rack A1", "Alcoa Howmet"),
    ("WT-ALU-003", "Lámina aluminio 6061 4x10 calibre .125", "Aluminio Bruto", None, 485.00, 22, 16, "Yard 1 — Rack A2", "Alcoa Howmet"),
    ("WT-ALU-004", "Diamond plate aluminio 4x8 calibre .100", "Aluminio Bruto", None, 268.00, 38, 18, "Yard 1 — Rack A2", "Alcoa Howmet"),
    ("WT-ALU-005", "Extrusión slat 1.5\" perforada Silverstar", "Aluminio Extruido", "Silverstar", 38.50, 420, 120, "Yard 1 — Bin B1", "Alcoa Howmet"),
    ("WT-ALU-006", "Extrusión riel superior 6\" anodizado", "Aluminio Extruido", "Silverstar", 92.00, 180, 60, "Yard 1 — Bin B2", "Alcoa Howmet"),
    ("WT-ALU-007", "Extrusión riel inferior Z-post 8\"", "Aluminio Extruido", "Pacesetter", 124.00, 95, 40, "Yard 1 — Bin B3", "Alcoa Howmet"),
    ("WT-ALU-008", "Tubo aluminio 2x4 pared .120", "Aluminio Extruido", None, 56.00, 240, 80, "Yard 1 — Bin B4", "Alcoa Howmet"),
    ("WT-ALU-009", "Tubo aluminio 2x6 pared .125", "Aluminio Extruido", "Roadbrute", 78.00, 168, 60, "Yard 1 — Bin B4", "Alcoa Howmet"),
    ("WT-ALU-010", "Plancha piso extruido HD 40\" Silverstar", "Aluminio Extruido", "Silverstar", 285.00, 64, 20, "Yard 1 — Rack A3", "Wilson Mill Sioux City"),

    # === EJES Y SUSPENSIÓN ===
    ("WT-AXL-100", "Eje Hendrickson INTRAAX AAT 25K", "Ejes y Suspensión", "Pacesetter", 3850.00, 18, 8, "WH-A — Rack 12", "Hendrickson USA"),
    ("WT-AXL-101", "Eje Hendrickson INTRAAX AANT 22.5K", "Ejes y Suspensión", "Silverstar", 3420.00, 22, 8, "WH-A — Rack 12", "Hendrickson USA"),
    ("WT-AXL-102", "Eje Hendrickson VANTRAAX HKANT 23K", "Ejes y Suspensión", "Roadbrute", 4180.00, 6, 4, "WH-A — Rack 13", "Hendrickson USA"),
    ("WT-AXL-103", "Eje Meritor TN-4671 22.5K", "Ejes y Suspensión", "Ranch Hand", 2640.00, 14, 6, "WH-A — Rack 13", "Meritor Inc"),
    ("WT-AXL-104", "Eje Reyco Granning RAR-240", "Ejes y Suspensión", "Roadbrute", 2980.00, 9, 4, "WH-A — Rack 13", "Reyco Granning"),
    ("WT-SUS-110", "Ballesta Hutchens H-9700 9-leaf", "Ejes y Suspensión", "Ranch Hand", 685.00, 38, 14, "WH-A — Rack 7", "Hutchens Industries"),
    ("WT-SUS-111", "Bolsa de aire Firestone W01-358-7039", "Ejes y Suspensión", None, 175.00, 96, 30, "WH-A — Rack 8", "Firestone Industrial"),
    ("WT-SUS-112", "Amortiguador Monroe Gas-Magnum 65", "Ejes y Suspensión", None, 88.00, 124, 40, "WH-A — Rack 8", "Monroe / Tenneco"),
    ("WT-SUS-113", "Kit U-bolt 7/8\" suspensión HD", "Ejes y Suspensión", None, 32.50, 320, 100, "WH-A — Bin 4", "Fastenal"),

    # === LLANTAS Y RUEDAS ===
    ("WT-WHL-200", "Llanta Michelin XZA2 11R22.5 LRH", "Llantas y Ruedas", None, 412.00, 64, 24, "WH-B — Bay 1", "Michelin North America"),
    ("WT-WHL-201", "Llanta Michelin X One Line 445/50R22.5", "Llantas y Ruedas", "Roadbrute", 685.00, 28, 12, "WH-B — Bay 1", "Michelin North America"),
    ("WT-WHL-202", "Llanta Bridgestone R268 Ecopia 11R22.5", "Llantas y Ruedas", None, 398.00, 52, 20, "WH-B — Bay 1", "Bridgestone Americas"),
    ("WT-WHL-203", "Llanta Bridgestone Greatec R197 445/50R22.5", "Llantas y Ruedas", None, 720.00, 22, 8, "WH-B — Bay 1", "Bridgestone Americas"),
    ("WT-WHL-204", "Rin Alcoa Dura-Bright EVO 22.5x8.25", "Llantas y Ruedas", None, 285.00, 88, 30, "WH-B — Bay 2", "Alcoa Wheels"),
    ("WT-WHL-205", "Rin Alcoa 22.5x9.00 forjado", "Llantas y Ruedas", None, 318.00, 42, 18, "WH-B — Bay 2", "Alcoa Wheels"),
    ("WT-WHL-206", "Rin Accuride acero 22.5x8.25", "Llantas y Ruedas", None, 145.00, 36, 16, "WH-B — Bay 2", "Accuride"),
    ("WT-WHL-207", "Tuercas rueda 33mm cromadas (set 10)", "Llantas y Ruedas", None, 48.00, 120, 30, "WH-B — Bin 3", "Spike Lug Nuts"),

    # === FRENOS Y ABS ===
    ("WT-BRK-300", "Sistema ABS Bendix EC-80 4S/2M", "Frenos", "Silverstar", 1240.00, 14, 6, "WH-C — Rack 3", "Bendix Commercial"),
    ("WT-BRK-301", "Sistema ABS Wabco TCS II 4S/2M", "Frenos", "Pacesetter", 1180.00, 10, 5, "WH-C — Rack 3", "Wabco / ZF"),
    ("WT-BRK-302", "Cámara freno Haldex GoldSeal 30/30", "Frenos", None, 165.00, 96, 30, "WH-C — Rack 4", "Haldex Group"),
    ("WT-BRK-303", "Cámara freno Haldex 36/36 HD", "Frenos", "Roadbrute", 195.00, 48, 16, "WH-C — Rack 4", "Haldex Group"),
    ("WT-BRK-304", "Tambor freno Webb Wheel 16.5x7", "Frenos", None, 215.00, 42, 16, "WH-C — Rack 5", "Webb Wheel"),
    ("WT-BRK-305", "Tambor freno Gunite 16.5x8.625 HD", "Frenos", "Roadbrute", 268.00, 24, 10, "WH-C — Rack 5", "Gunite"),
    ("WT-BRK-306", "Forros freno MGM Q-Plus FF", "Frenos", None, 78.00, 168, 50, "WH-C — Rack 6", "MGM Brakes"),
    ("WT-BRK-307", "Disco freno Meritor EX+ 17\"", "Frenos", "Pacesetter", 385.00, 8, 4, "WH-C — Rack 5", "Meritor Inc"),
    ("WT-BRK-308", "Válvula relay Bendix R-14", "Frenos", None, 92.00, 34, 12, "WH-C — Bin 9", "Bendix Commercial"),

    # === ELÉCTRICO Y ILUMINACIÓN ===
    ("WT-ELE-400", "Faro LED rojo trasero Grote LED44", "Eléctrico", None, 38.00, 280, 80, "WH-E — Rack 1", "Grote Industries"),
    ("WT-ELE-401", "Faro LED ámbar lateral Truck-Lite Super 44", "Eléctrico", None, 22.00, 360, 100, "WH-E — Rack 1", "Truck-Lite"),
    ("WT-ELE-402", "Faro LED stop/tail/turn Truck-Lite 60-series", "Eléctrico", None, 42.00, 184, 60, "WH-E — Rack 1", "Truck-Lite"),
    ("WT-ELE-403", "Faro LED clearance Peterson PM168A", "Eléctrico", None, 14.50, 420, 120, "WH-E — Rack 1", "Peterson MFG"),
    ("WT-ELE-404", "Faro LED interior Optronics dome", "Eléctrico", "Silverstar", 28.00, 86, 30, "WH-E — Rack 2", "Optronics"),
    ("WT-ELE-405", "Arnés ABS Phillips QCMS2 7-way", "Eléctrico", None, 145.00, 48, 18, "WH-E — Rack 2", "Phillips Industries"),
    ("WT-ELE-406", "Conector espiral Permalogic 12ft", "Eléctrico", None, 68.00, 92, 24, "WH-E — Rack 2", "Phillips Industries"),
    ("WT-ELE-407", "Caja recibidora Phillips Sta-Dry", "Eléctrico", None, 52.00, 78, 24, "WH-E — Bin 3", "Phillips Industries"),
    ("WT-ELE-408", "Arnés principal 50ft 16AWG 7-cond", "Eléctrico", None, 89.00, 64, 20, "WH-E — Rack 2", "Phillips Industries"),

    # === LIVESTOCK ESPECÍFICO ===
    ("WT-LIV-500", "Compuerta divisora central ganado Silverstar", "Livestock", "Silverstar", 485.00, 14, 6, "WH-G — Livestock", "Wilson Mill Sioux City"),
    ("WT-LIV-501", "Gate cortadora plegable cattle 48\"", "Livestock", "Silverstar", 320.00, 22, 8, "WH-G — Livestock", "Wilson Mill Sioux City"),
    ("WT-LIV-502", "Rampa carga aluminio plegable Ranch Hand", "Livestock", "Ranch Hand", 1240.00, 5, 3, "WH-G — Livestock", "Wilson Mill Sioux City"),
    ("WT-LIV-503", "Cattle cleats antideslizantes (set 12)", "Livestock", "Silverstar", 145.00, 64, 20, "WH-G — Bin 1", "Roppe"),
    ("WT-LIV-504", "Piso goma hog matting 4x8", "Livestock", "Silverstar", 88.00, 38, 16, "WH-G — Bin 2", "Roppe"),
    ("WT-LIV-505", "Jail bar slat partition aluminio", "Livestock", "Silverstar", 92.00, 84, 24, "WH-G — Rack 3", "Wilson Mill Sioux City"),
    ("WT-LIV-506", "Belly gate hog deck plegable", "Livestock", "Silverstar", 580.00, 8, 4, "WH-G — Rack 4", "Wilson Mill Sioux City"),
    ("WT-LIV-507", "Drop floor mechanism set Silverstar", "Livestock", "Silverstar", 845.00, 4, 3, "WH-G — Rack 4", "Wilson Mill Sioux City"),

    # === GRAIN ESPECÍFICO ===
    ("WT-GRN-600", "Trampilla descarga Aulick hidráulica 24\"", "Grain", "Pacesetter", 985.00, 7, 4, "WH-G — Grain", "Aulick Industries"),
    ("WT-GRN-601", "Trap valve Walinga 200-series", "Grain", "Pacesetter", 845.00, 6, 3, "WH-G — Grain", "Walinga"),
    ("WT-GRN-602", "Lona enrollable Shur-Co 4500 HD", "Grain", "Pacesetter", 1450.00, 4, 3, "WH-G — Grain", "Shur-Co LLC"),
    ("WT-GRN-603", "Sistema Shur-Lok aluminio 40ft", "Grain", "Pacesetter", 685.00, 9, 4, "WH-G — Grain", "Shur-Co LLC"),
    ("WT-GRN-604", "Mirilla aluminio Bee-Lite 4\"", "Grain", "Pacesetter", 65.00, 38, 14, "WH-G — Bin 5", "Bee-Lite"),
    ("WT-GRN-605", "Escalera lateral aluminio 12-step", "Grain", "Pacesetter", 245.00, 18, 8, "WH-G — Rack 6", "Wilson Mill Sioux City"),
    ("WT-GRN-606", "Aro tolva hopper neumático 14\"", "Grain", "Pacesetter", 178.00, 14, 6, "WH-G — Rack 6", "Wilson Mill Sioux City"),
    ("WT-GRN-607", "Indicador nivel grano ROTO-DRO 360", "Grain", "Pacesetter", 92.00, 22, 10, "WH-G — Bin 7", "Walinga"),

    # === FLATBED / ROADBRUTE ===
    ("WT-FLB-700", "Piso roble Apitong 1.5\" 48\" plank", "Pisos", "Roadbrute", 145.00, 28, 12, "WH-D — Pisos", "Wilson Mill Sioux City"),
    ("WT-FLB-701", "Sliding tandem rail Holland SAF-T-LITE", "Flatbed", "Roadbrute", 985.00, 6, 3, "WH-D — Rack 8", "SAF-Holland"),
    ("WT-FLB-702", "Stake pocket aluminio HD (par)", "Flatbed", "Roadbrute", 32.00, 168, 50, "WH-D — Bin 10", "Buyers Products"),
    ("WT-FLB-703", "Winch ratchet 4\" deck Kinedyne", "Flatbed", "Roadbrute", 78.00, 96, 30, "WH-D — Rack 9", "Kinedyne"),
    ("WT-FLB-704", "Tie-down ring D-ring weld-on", "Flatbed", "Roadbrute", 14.50, 280, 80, "WH-D — Bin 10", "Buyers Products"),
    ("WT-FLB-705", "Headache rack aluminio Commander", "Flatbed", "Commander", 685.00, 4, 3, "WH-D — Rack 11", "Wilson Mill Sioux City"),

    # === KING PIN / LANDING GEAR / COUPLINGS ===
    ("WT-CPL-800", "King pin SAF-Holland 2.0\" Class A", "Acoplamientos", None, 285.00, 22, 8, "WH-H — Rack 1", "SAF-Holland"),
    ("WT-CPL-801", "Landing gear Holland Mark V 2-speed", "Acoplamientos", None, 685.00, 12, 6, "WH-H — Rack 1", "SAF-Holland"),
    ("WT-CPL-802", "Pata jack hidráulica Jost A480", "Acoplamientos", None, 545.00, 8, 4, "WH-H — Rack 2", "Jost International"),
    ("WT-CPL-803", "Pintle hook Buyers 50-ton", "Acoplamientos", None, 248.00, 14, 6, "WH-H — Rack 2", "Buyers Products"),
    ("WT-CPL-804", "Glad hand red EM SAF-T", "Acoplamientos", None, 18.00, 240, 60, "WH-H — Bin 3", "Phillips Industries"),
    ("WT-CPL-805", "Glad hand blue SR SAF-T", "Acoplamientos", None, 18.00, 240, 60, "WH-H — Bin 3", "Phillips Industries"),

    # === NEUMÁTICO ===
    ("WT-AIR-900", "Manguera nylon 1/2\" rojo DOT (100ft)", "Sistemas Neumáticos", None, 128.00, 24, 10, "WH-C — Rack 8", "Parker Hannifin"),
    ("WT-AIR-901", "Manguera nylon 1/2\" azul DOT (100ft)", "Sistemas Neumáticos", None, 128.00, 24, 10, "WH-C — Rack 8", "Parker Hannifin"),
    ("WT-AIR-902", "Tanque aire aluminio 2200ci", "Sistemas Neumáticos", None, 245.00, 18, 6, "WH-C — Rack 9", "Haldex Group"),
    ("WT-AIR-903", "Tanque aire acero 3000ci", "Sistemas Neumáticos", "Roadbrute", 168.00, 16, 8, "WH-C — Rack 9", "Haldex Group"),
    ("WT-AIR-904", "Fitting brass Push-Lok 1/2\" (set 25)", "Sistemas Neumáticos", None, 38.00, 84, 24, "WH-C — Bin 10", "Parker Hannifin"),

    # === PINTURA Y FINISH ===
    ("WT-PNT-A00", "Pintura Champion Red Wilson 5gal", "Pintura y Acabados", None, 285.00, 18, 6, "WH-F — Pintura", "Sherwin Williams"),
    ("WT-PNT-A01", "Pintura Wilson White 5gal", "Pintura y Acabados", None, 265.00, 22, 6, "WH-F — Pintura", "Sherwin Williams"),
    ("WT-PNT-A02", "Primer epóxico 2K 1gal", "Pintura y Acabados", None, 78.00, 32, 10, "WH-F — Pintura", "PPG Industries"),
    ("WT-PNT-A03", "Clearcoat poliuretano 1gal", "Pintura y Acabados", None, 92.00, 28, 8, "WH-F — Pintura", "PPG Industries"),
    ("WT-PNT-A04", "Cinta reflectiva 3M DOT-C2 (150ft)", "Pintura y Acabados", None, 145.00, 42, 12, "WH-F — Rack 1", "3M"),
    ("WT-PNT-A05", "Decal Wilson Trailers logo grande", "Pintura y Acabados", None, 38.00, 124, 30, "WH-F — Bin 2", "Wilson Mill Sioux City"),
    ("WT-PNT-A06", "Sellador 3M VHB doble cara (roll)", "Pintura y Acabados", None, 68.00, 42, 14, "WH-F — Bin 3", "3M"),

    # === HARDWARE ===
    ("WT-HRD-B00", "Tornillería kit ensamblaje Silverstar", "Hardware", "Silverstar", 145.00, 56, 16, "WH-E — Rack 5", "Fastenal"),
    ("WT-HRD-B01", "Tornillería kit ensamblaje Pacesetter", "Hardware", "Pacesetter", 168.00, 32, 12, "WH-E — Rack 5", "Fastenal"),
    ("WT-HRD-B02", "Bisagra puerta trasera HD inox", "Hardware", "Silverstar", 92.00, 28, 12, "WH-E — Rack 5", "Wilson Mill Sioux City"),
    ("WT-HRD-B03", "Cerradura compuerta cam-lock inox", "Hardware", "Pacesetter", 165.00, 22, 8, "WH-E — Rack 6", "Buyers Products"),
    ("WT-HRD-B04", "Remache estructural 1/4\" inox (caja 500)", "Hardware", None, 78.00, 96, 30, "WH-E — Bin 7", "Avdel / Stanley"),
    ("WT-HRD-B05", "Remache 3/16\" aluminio (caja 1000)", "Hardware", None, 42.00, 168, 40, "WH-E — Bin 7", "POP / Stanley"),
    ("WT-HRD-B06", "Mud flap reinforced 24x30 Wilson logo", "Hardware", None, 28.50, 280, 60, "WH-E — Bin 8", "Buyers Products"),
    ("WT-HRD-B07", "Soporte mud flap stainless", "Hardware", None, 24.00, 240, 60, "WH-E — Bin 8", "Buyers Products"),
    ("WT-HRD-B08", "ICC rear impact guard DOT-compliant", "Hardware", "Roadbrute", 285.00, 14, 6, "WH-E — Rack 9", "Wilson Mill Sioux City"),
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
    ("Nómina taller — soldadores", "Salarios soldadores MIG/TIG planta Sioux City", 18500, 32000),
    ("Nómina taller — armadores", "Salarios armadores línea principal", 14200, 26800),
    ("Nómina administrativa", "Personal oficinas + ingeniería", 22000, 38000),
    ("Energía eléctrica", "MidAmerican Energy — consumo planta", 4200, 9800),
    ("Gas natural", "Suministro hornos pintura + calefacción", 1800, 4400),
    ("Mantenimiento maquinaria", "Servicio prensa hidráulica + dobladoras", 450, 2800),
    ("Mantenimiento cabina pintura", "Servicio cabina + filtros HEPA", 380, 1850),
    ("Combustible flota", "Diesel flota interna", 280, 1200),
    ("Transporte interno", "Flete entre plantas (Sioux/Yankton/Moberly)", 850, 3400),
    ("Suministros oficina", "Material consumible administrativo", 120, 580),
    ("Suministros taller — consumibles", "Discos corte, electrodos, abrasivos", 420, 2200),
    ("EPP — Equipo protección", "Caretas soldar, guantes, botas, lentes", 285, 1400),
    ("Internet y telefonía", "Servicio mensual planta + oficinas", 380, 720),
    ("Seguros planta + flota", "Travelers Insurance prima mensual", 4200, 6800),
    ("Capacitación", "Certificación AWS D1.2 aluminio", 600, 2400),
    ("Marketing", "Pauta digital + Mid-America Trucking Show", 900, 4500),
    ("R&D ingeniería", "Diseño nuevos modelos + prototipos", 1800, 7500),
]

PAID_TO_POOL = [
    "MidAmerican Energy", "Black Hills Energy", "CenturyLink Business",
    "Sioux City Auto Parts", "United Rentals", "Office Depot",
    "Wells Fargo Bank", "Travelers Insurance", "ADP Payroll",
    "Northland Welding Supply", "Praxair", "Lincoln Electric",
    "FedEx Freight", "Old Dominion Freight",
    "Mid-America Trucking Show LLC", "Verizon Business",
    "Grainger Industrial Supply", "MSC Direct", "Nómina interna",
]


# Bill-of-Materials por línea de tráiler (cantidades por UN tráiler).
# Diseñado para que casi todas las partes de inventario participen.
BOMS = {
    "Silverstar": [
        # Estructura aluminio
        ("WT-ALU-002", 8), ("WT-ALU-005", 24), ("WT-ALU-006", 4),
        ("WT-ALU-010", 6),
        # Tren rodante
        ("WT-AXL-101", 2), ("WT-SUS-111", 4), ("WT-SUS-112", 4),
        ("WT-SUS-113", 4),
        # Ruedas
        ("WT-WHL-200", 8), ("WT-WHL-204", 8), ("WT-WHL-207", 1),
        # Frenos
        ("WT-BRK-300", 1), ("WT-BRK-302", 4), ("WT-BRK-304", 4),
        ("WT-BRK-306", 4), ("WT-BRK-308", 1),
        # Eléctrico
        ("WT-ELE-400", 4), ("WT-ELE-401", 8), ("WT-ELE-403", 12),
        ("WT-ELE-404", 2), ("WT-ELE-405", 1), ("WT-ELE-406", 1),
        ("WT-ELE-408", 1),
        # Livestock
        ("WT-LIV-500", 1), ("WT-LIV-501", 2), ("WT-LIV-503", 1),
        ("WT-LIV-505", 6), ("WT-LIV-507", 1),
        # Couplings/aire
        ("WT-CPL-800", 1), ("WT-CPL-801", 2), ("WT-CPL-804", 1),
        ("WT-CPL-805", 1), ("WT-AIR-900", 1), ("WT-AIR-901", 1),
        ("WT-AIR-902", 2), ("WT-AIR-904", 1),
        # Pintura
        ("WT-PNT-A00", 1), ("WT-PNT-A01", 0.5), ("WT-PNT-A02", 1),
        ("WT-PNT-A03", 1), ("WT-PNT-A04", 1), ("WT-PNT-A05", 2),
        # Hardware
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
        ("WT-CPL-800", 1), ("WT-CPL-801", 2), ("WT-CPL-804", 1),
        ("WT-CPL-805", 1), ("WT-AIR-900", 1), ("WT-AIR-901", 1),
        ("WT-AIR-902", 1),
        ("WT-PNT-A00", 1), ("WT-PNT-A02", 1), ("WT-PNT-A04", 1),
        ("WT-PNT-A05", 2),
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
        ("WT-CPL-800", 1), ("WT-CPL-801", 2), ("WT-CPL-804", 1),
        ("WT-CPL-805", 1), ("WT-AIR-900", 1), ("WT-AIR-901", 1),
        ("WT-AIR-902", 2),
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
        ("WT-CPL-800", 1), ("WT-CPL-801", 2), ("WT-CPL-804", 1),
        ("WT-CPL-805", 1), ("WT-AIR-900", 1), ("WT-AIR-901", 1),
        ("WT-AIR-903", 2),
        ("WT-PNT-A00", 1), ("WT-PNT-A02", 1), ("WT-PNT-A04", 1),
        ("WT-PNT-A05", 2),
        ("WT-HRD-B04", 2), ("WT-HRD-B06", 4), ("WT-HRD-B07", 4),
        ("WT-HRD-B08", 1),
    ],
}


def run():
    db = SessionLocal()
    # wipe
    db.query(models.WorkOrder).delete()
    db.query(models.BOMLine).delete()
    db.query(models.StockMovement).delete()
    db.query(models.PurchaseItem).delete()
    db.query(models.Purchase).delete()
    db.query(models.Expense).delete()
    db.query(models.Product).delete()
    db.commit()

    # Products
    for sku, name, cat, line, cost, stock, mn, loc, sup in PRODUCTS:
        db.add(models.Product(
            sku=sku, name=name, category=cat, trailer_line=line,
            unit_cost=cost, stock=stock, min_stock=mn,
            location=loc, supplier=sup,
        ))
    db.commit()

    products = db.query(models.Product).all()
    by_sku = {p.sku: p for p in products}

    # BoMs
    for line, items in BOMS.items():
        for sku, qty in items:
            p = by_sku.get(sku)
            if not p:
                continue
            db.add(models.BOMLine(trailer_line=line, product_id=p.id, quantity=qty))
    db.commit()

    now = datetime.utcnow()

    # Purchases — last 240 days (8 months) for richer charts
    for i in range(160):
        day_offset = random.randint(0, 240)
        date = now - timedelta(days=day_offset, hours=random.randint(0, 8))
        po = f"PO-2026-{1000 + i:04d}"
        vendor = random.choice(VENDORS)
        purchase = models.Purchase(
            po_number=po, vendor=vendor, date=date,
            status="received", total=0.0,
            notes=f"Reposición — {vendor}",
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
                reason=f"Compra {po}", reference=po,
            ))
        purchase.total = round(total, 2)
    db.commit()

    # Expenses — last 240 days
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

    # Work orders — simulate historical trailer productions across 8 months
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
                reason=f"Producción {line} {wo_num}",
                reference=wo_num,
            ))
        db.add(models.WorkOrder(
            wo_number=wo_num, trailer_line=line, quantity=qty,
            date=date, status="completed",
            material_cost=round(material_cost, 2),
        ))
    db.commit()

    # Refresh stock counts from movements (start from PRODUCTS initial then apply net)
    # Rebuild stock = initial_stock + sum(IN) - sum(OUT) across movements
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

    print("[OK] Seed completo — Wilson Trailer Co.")
    print(f"  Productos:   {db.query(models.Product).count()}")
    print(f"  BoM lines:   {db.query(models.BOMLine).count()}")
    print(f"  Compras:     {db.query(models.Purchase).count()}")
    print(f"  Gastos:      {db.query(models.Expense).count()}")
    print(f"  Work orders: {db.query(models.WorkOrder).count()}")
    print(f"  Movimientos: {db.query(models.StockMovement).count()}")


if __name__ == "__main__":
    run()
