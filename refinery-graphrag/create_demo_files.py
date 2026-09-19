#!/usr/bin/env python3
"""
DEMO P&ID GENERATOR
Creates synthetic piping diagrams with equipment tags for testing
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

def create_demo_pid(output_path="demo_blueprint.png"):
    """
    Generate a realistic-looking P&ID diagram with equipment tags
    """
    
    # Create white canvas
    width, height = 1200, 800
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Try to use a nice font, fallback to default
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except:
        try:
            font_large = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 16)
            font_small = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 12)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
    
    # Draw title
    draw.text((50, 20), "PIPING & INSTRUMENTATION DIAGRAM (P&ID)", fill='black', font=font_large)
    draw.line([(50, 50), (width-50, 50)], fill='black', width=2)
    
    # Equipment definitions: (name, x, y, symbol_type)
    equipment = [
        # Pumps
        ("PMP-201", 150, 150, "pump"),
        
        # Valves
        ("VLV-104", 300, 150, "valve"),
        ("VLV-105", 450, 200, "valve"),
        
        # Motors
        ("MTR-301", 600, 150, "motor"),
        
        # Sensors
        ("SEN-401", 750, 120, "sensor"),
        
        # Vessels
        ("VSL-501", 900, 200, "vessel"),
        
        # Heat Exchanger
        ("HEX-601", 300, 400, "heatex"),
        
        # More equipment
        ("VLV-106", 500, 350, "valve"),
        ("PMP-202", 700, 350, "pump"),
    ]
    
    # Draw piping lines (connections)
    # Main horizontal line
    draw.line([(100, 170), (1100, 170)], fill='black', width=3)
    
    # Secondary lines
    draw.line([(350, 170), (350, 300)], fill='black', width=3)
    draw.line([(300, 300), (500, 300)], fill='black', width=3)
    draw.line([(700, 300), (750, 300)], fill='black', width=3)
    draw.line([(900, 170), (900, 350)], fill='black', width=3)
    
    # Draw equipment symbols
    for tag, x, y, equipment_type in equipment:
        draw_equipment(draw, x, y, equipment_type, tag, font_small)
    
    # Add legend
    legend_y = 600
    draw.text((50, legend_y), "LEGEND:", fill='black', font=font_large)
    
    legend_items = [
        ("●", "Valve (VLV-XXX)"),
        ("○", "Pump (PMP-XXX)"),
        ("□", "Sensor (SEN-XXX)"),
        ("≈", "Heat Exchanger (HEX-XXX)"),
        ("⬜", "Vessel (VSL-XXX)"),
        ("⚙", "Motor (MTR-XXX)"),
    ]
    
    for i, (symbol, label) in enumerate(legend_items):
        y_pos = legend_y + 30 + (i * 25)
        draw.text((70, y_pos), f"{symbol}  {label}", fill='black', font=font_small)
    
    # Add some realistic P&ID annotations
    draw.text((150, 700), "Flow Direction →", fill='#666666', font=font_small)
    draw.text((700, 700), "Document: PID-001-REV-A", fill='#666666', font=font_small)
    draw.text((50, 750), "Industrial Plant - Unit 01", fill='#666666', font=font_small)
    
    # Save
    image.save(output_path)
    print(f"✓ Created demo P&ID: {output_path}")
    return output_path

def draw_equipment(draw, x, y, equipment_type, tag, font):
    """Draw equipment symbol and tag"""
    
    if equipment_type == "pump":
        # Draw circle for pump
        draw.ellipse([x-15, y-15, x+15, y+15], outline='black', width=2)
        draw.line([(x-10, y), (x+10, y)], fill='black', width=2)
        
    elif equipment_type == "valve":
        # Draw triangle/wedge for valve
        points = [(x, y-12), (x-12, y+8), (x+12, y+8)]
        draw.polygon(points, outline='black', fill='white')
        
    elif equipment_type == "motor":
        # Draw square for motor
        draw.rectangle([x-12, y-12, x+12, y+12], outline='black', width=2)
        draw.text((x-4, y-4), "M", fill='black', font=font)
        
    elif equipment_type == "sensor":
        # Draw small circle for sensor
        draw.ellipse([x-8, y-8, x+8, y+8], outline='black', width=2, fill='gray')
        
    elif equipment_type == "vessel":
        # Draw rectangle for vessel
        draw.rectangle([x-20, y-15, x+20, y+15], outline='black', width=2)
        
    elif equipment_type == "heatex":
        # Draw wavy lines for heat exchanger
        for i in range(4):
            draw.line([(x-15, y-10+i*5), (x+15, y-10+i*5)], fill='black', width=2)
    
    # Draw tag label
    draw.text((x-20, y+25), tag, fill='#0066cc', font=font)

def create_test_manual():
    """Create a test SOP document"""
    
    manual_content = """STANDARD OPERATING PROCEDURES
IOCL Refinery Unit 01 - Revision A

EQUIPMENT SPECIFICATIONS

VLV-104 SAFETY RELIEF VALVE
Classification: Pressure Relief Valve (PRV)
Service: Crude Oil Processing
Standard Purge Pressure: 45 PSI
Maximum Operating Pressure: 50 PSI
Minimum Operating Pressure: 10 PSI
Operational Temperature Range: 10°C to 120°C
Body Material: Carbon Steel ASTM A105
Valve Seat: Stainless Steel
Spring Range: 30-60 PSI
Flow Capacity: 500 GPM nominal
Inlet Connection: 2" NPT
Outlet Connection: 2" NPT
Maintenance Interval: 6 months
Seal Type: Bonnet seal
Manual Override: Red colored handwheel
Emergency Response: If pressure exceeds 55 PSI, activate emergency shutdown sequence SOP-EM-001
Last Maintenance: 2024-01-15
Next Due: 2024-07-15

PMP-201 CENTRIFUGAL PUMP
Type: Horizontal Centrifugal Pump
Manufacturer: Flowserve
Model: FGLC Type
Service Fluid: Crude Oil
Nominal Flow Rate: 200 GPM
Maximum Flow Rate: 220 GPM
Discharge Head: 150 feet (51.8 bar)
Inlet Pressure: Atmospheric
Outlet Pressure: 50 PSI operating
Motor Size: 75 HP
Motor Speed: 1800 RPM
Shaft Seal: Mechanical Dual Cartridge Seal
Bearing Type: Ball bearings, grease lubricated
Vibration Limit: 0.2 inches/second (ISO 20816)
Temperature Monitoring: Installed on bearing
Lubrication Schedule: Every 500 hours
Critical Speed: 2100 RPM
Cavitation NPSH Required: 5 feet

MTR-301 MAIN DRIVE MOTOR
Type: Three-Phase AC Induction Motor
Power Rating: 75 HP
Voltage: 480V AC, 60 Hz
Current Rating: 85 Amperes full load
Efficiency: 95% (NEMA Premium)
Cooling Method: Ambient air cooling (ODP enclosure)
Insulation Class: F
Duty Cycle: Continuous
Bearing Type: Deep groove ball bearings
Lubrication: Grease type NLGI Grade 2
Temperature Rise: 80°C above ambient
Thermal Overload Protection: Built-in PTC thermistor
Starting Method: Soft starter (30 second ramp)
Control Voltage: 24V DC
Emergency Stop: Red mushroom button
Maintenance: Annual bearing relubrication (250 ml)
Last Service: 2024-01-20

SEN-401 PRESSURE TRANSMITTER
Type: Electronic Pressure Transmitter
Measurement Range: 0-100 PSI
Output Signal: 4-20 mA DC
Accuracy: ±0.5% FS
Response Time: <100 milliseconds
Process Connection: 1/2" NPT Male
Supply Voltage: 24V DC ±10%
IP Rating: IP67 (fully sealed)
Mounting: Direct to process
Calibration: Annually required
Alarm Setpoints: Low=20 PSI, High=80 PSI

SAFETY PROCEDURES

Pressure Relief - SOP-001:
1. Never manually override VLV-104 unless emergency
2. Check pressure gauge reading before operation
3. If gauge reads >55 PSI:
   - Stop PMP-201 immediately
   - Open VLV-104 manual handwheel
   - Activate alarm bell (switch on wall)
   - Contact Shift Supervisor immediately

Motor Operation - SOP-002:
1. Verify all connections before starting MTR-301
2. Check for any unusual vibration (>0.2 in/sec stops operation)
3. Monitor temperature gauge (max 80°C)
4. Soft starter will automatically ramp speed over 30 seconds

Equipment Inspection Checklist:
□ PMP-201: Check for leaks daily
□ VLV-104: Inspect for corrosion weekly
□ MTR-301: Verify cooling air flow monthly
□ SEN-401: Check calibration quarterly

EMERGENCY CONTACTS
Shift Supervisor: Ext. 2001
Safety Officer: Ext. 2002
Maintenance: Ext. 2003
Medical: Ext. 2010
"""
    
    filepath = "test_manual.txt"
    with open(filepath, 'w') as f:
        f.write(manual_content)
    
    print(f"✓ Created test manual: {filepath}")
    return filepath

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════╗
    ║  P&ID DEMO GENERATOR                       ║
    ║  Creates test images and documents         ║
    ╚════════════════════════════════════════════╝
    """)
    
    # Create demo P&ID image
    create_demo_pid("demo_blueprint.png")
    
    # Create test manual
    create_test_manual()
    
    print("\n✓ Demo files created!")
    print("  - demo_blueprint.png (P&ID image)")
    print("  - test_manual.txt (SOP document)")
    print("\nTo test the system:")
    print("  1. Start backend: python app.py")
    print("  2. Open index.html in browser")
    print("  3. Upload demo_blueprint.png")
    print("  4. Ask: 'What is VLV-104?'")
