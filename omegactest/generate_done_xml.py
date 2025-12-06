import argparse
import time
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import sys

def generate_done_xml(args):
    root = ET.Element("Done")
    
    ET.SubElement(root, "buildId").text = args.build_id
    
    # Use provided time or current time
    timestamp = args.time if args.time else str(int(time.time()))
    ET.SubElement(root, "time").text = timestamp

    # Pretty print
    xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="\t")
    
    with open(args.output, "w") as f:
        f.write(xmlstr)
    
    print(f"Generated {args.output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Done.xml for CDash")
    parser.add_argument("--build-id", required=True, help="ID of the build")
    parser.add_argument("--time", help="Time of build (epoch). Default is current time.")
    parser.add_argument("--output", default="Done.xml", help="Output filename")
    
    args = parser.parse_args()
    generate_done_xml(args)
