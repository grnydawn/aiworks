import argparse
import platform
import time
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import sys
import random
import base64
import gzip

def get_system_info():
    info = {}
    info['OSName'] = platform.system()
    info['Hostname'] = platform.node()
    info['OSRelease'] = platform.release()
    info['OSVersion'] = platform.version()
    info['OSPlatform'] = platform.machine()
    info['Is64Bits'] = "1" if sys.maxsize > 2**32 else "0"
    
    try:
        import psutil
        info['NumberOfLogicalCPU'] = str(psutil.cpu_count(logical=True))
        info['NumberOfPhysicalCPU'] = str(psutil.cpu_count(logical=False))
        info['TotalPhysicalMemory'] = str(int(psutil.virtual_memory().total / (1024 * 1024)))
    except ImportError:
        info['NumberOfLogicalCPU'] = "1"
        info['NumberOfPhysicalCPU'] = "1"
        info['TotalPhysicalMemory'] = "1024"

    info['VendorString'] = "Unknown"
    info['VendorID'] = "Unknown"
    info['FamilyID'] = "0"
    info['ModelID'] = "0"
    info['ProcessorCacheSize'] = "0"
    info['ProcessorClockFrequency'] = "0"
    
    return info

def split_escaped(text, separator, maxsplit):
    parts = []
    last_pos = 0
    current_pos = 0
    splits = 0
    
    while splits < maxsplit:
        idx = text.find(separator, current_pos)
        if idx == -1:
            break
            
        # Check backslashes before idx
        backslashes = 0
        check_idx = idx - 1
        while check_idx >= 0 and text[check_idx] == '\\':
            backslashes += 1
            check_idx -= 1
            
        if backslashes % 2 == 0:
            # Even backslashes, so separator is NOT escaped
            parts.append(text[last_pos:idx])
            last_pos = idx + len(separator)
            current_pos = last_pos
            splits += 1
        else:
            # Odd backslashes, separator IS escaped
            current_pos = idx + 1
            
    parts.append(text[last_pos:])
    return parts

def unescape(text, separator):
    # Replace escaped separator with separator
    # Replace escaped backslash with backslash
    # Order matters: first unescape the separator, then the backslash
    return text.replace('\\' + separator, separator).replace('\\\\', '\\')

def generate_test_xml(args):
    sys_info = get_system_info()
    
    site = ET.Element("Site")
    site.set("BuildName", args.build_name)
    site.set("BuildStamp", args.build_stamp)
    site.set("Name", args.site_name)
    site.set("Generator", "ctest-3.24.2")
    site.set("CompilerName", "")
    site.set("CompilerVersion", "")
    
    for key, value in sys_info.items():
        site.set(key, value)

    testing = ET.SubElement(site, "Testing")
    
    start_time = int(time.time())
    ET.SubElement(testing, "StartDateTime").text = time.ctime(start_time)
    ET.SubElement(testing, "StartTestTime").text = str(start_time)
    
    test_list = ET.SubElement(testing, "TestList")
    
    parsed_tests = []
    if args.test:
        for test_str in args.test:
            parts = split_escaped(test_str, args.separator, 2)
            
            if len(parts) < 3:
                # Fallback/Defaults
                if len(parts) == 1:
                    name = parts[0]
                    status = "passed"
                    output = "No output provided"
                elif len(parts) == 2:
                    name = parts[0]
                    status = parts[1]
                    output = "No output provided"
                else:
                    name = "Unknown"
                    status = "failed"
                    output = "Invalid format"
            else:
                name = parts[0]
                status = parts[1]
                output = parts[2]
            
            # Unescape content
            name = unescape(name, args.separator)
            status = unescape(status, args.separator)
            output = unescape(output, args.separator)
            
            parsed_tests.append({'name': name, 'status': status, 'output': output})
            ET.SubElement(test_list, "Test").text = f"./cdash_examples/test/{name}"
        
    for test_data in parsed_tests:
        test_name = test_data['name']
        status = test_data['status']
        output_text = test_data['output']
        
        test_elem = ET.SubElement(testing, "Test", Status=status)
        ET.SubElement(test_elem, "Name").text = test_name
        ET.SubElement(test_elem, "Path").text = "./cdash_examples/test"
        ET.SubElement(test_elem, "FullName").text = f"./cdash_examples/test/{test_name}"
        ET.SubElement(test_elem, "FullCommandLine").text = f"./cdash_examples/test/{test_name} --run"
        
        results = ET.SubElement(test_elem, "Results")
        
        # Execution Time
        exec_time = random.uniform(0.1, 2.0)
        named_meas_time = ET.SubElement(results, "NamedMeasurement", type="numeric/double", name="Execution Time")
        ET.SubElement(named_meas_time, "Value").text = f"{exec_time:.6f}"
        
        # Completion Status
        named_meas_status = ET.SubElement(results, "NamedMeasurement", type="text/string", name="Completion Status")
        ET.SubElement(named_meas_status, "Value").text = "Completed"
        
        # Command Line
        named_meas_cmd = ET.SubElement(results, "NamedMeasurement", type="text/string", name="Command Line")
        ET.SubElement(named_meas_cmd, "Value").text = f"./cdash_examples/test/{test_name} --run"
        
        # Measurement (Output)
        measurement = ET.SubElement(results, "Measurement")
        
        # Compress and base64 encode output
        compressed_output = gzip.compress(output_text.encode('utf-8'))
        b64_output = base64.b64encode(compressed_output).decode('utf-8')
        
        ET.SubElement(measurement, "Value", encoding="base64", compression="gzip").text = b64_output

    ET.SubElement(testing, "EndDateTime").text = time.ctime(int(time.time()))
    ET.SubElement(testing, "EndTestTime").text = str(int(time.time()))
    
    # Pretty print
    xmlstr = minidom.parseString(ET.tostring(site)).toprettyxml(indent="\t")
    
    with open(args.output, "w") as f:
        f.write(xmlstr)
    
    print(f"Generated {args.output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Test.xml for CDash")
    parser.add_argument("--build-name", required=True, help="Name of the build")
    parser.add_argument("--build-stamp", required=True, help="Build stamp")
    parser.add_argument("--site-name", required=True, help="Name of the site")
    parser.add_argument("--test", action='append', help="Test info in format 'Name:Status:Output' (can be repeated). Use --separator to change delimiter.")
    parser.add_argument("--separator", default=":", help="Separator for test info (default: ':'). Supports escaping with backslash.")
    parser.add_argument("--output", default="Test.xml", help="Output filename")
    
    args = parser.parse_args()
    generate_test_xml(args)
