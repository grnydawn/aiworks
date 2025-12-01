import argparse
import platform
import time
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import sys

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
        info['TotalPhysicalMemory'] = str(int(psutil.virtual_memory().total / (1024 * 1024))) # MB
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

def parse_build_issue(issue_str, separator, index):
    # Format: Text:SourceFile:SourceLineNumber:BuildLogLine:PreContext:PostContext:RepeatCount
    # Max split 6 to get 7 parts
    parts = split_escaped(issue_str, separator, 6)
    
    # Defaults
    text = parts[0] if len(parts) > 0 else "Unknown Issue"
    source_file = parts[1] if len(parts) > 1 and parts[1] else "./cdash_examples/dummy_file.c"
    source_line = parts[2] if len(parts) > 2 and parts[2] else "0"
    build_log_line = parts[3] if len(parts) > 3 and parts[3] else str(index + 1)
    pre_context = parts[4] if len(parts) > 4 else ""
    post_context = parts[5] if len(parts) > 5 else ""
    repeat_count = parts[6] if len(parts) > 6 and parts[6] else "0"
    
    return {
        'Text': unescape(text, separator),
        'SourceFile': unescape(source_file, separator),
        'SourceLineNumber': unescape(source_line, separator),
        'BuildLogLine': unescape(build_log_line, separator),
        'PreContext': unescape(pre_context, separator),
        'PostContext': unescape(post_context, separator),
        'RepeatCount': unescape(repeat_count, separator)
    }

def generate_build_xml(args):
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

    build = ET.SubElement(site, "Build")
    
    start_time = int(time.time())
    ET.SubElement(build, "StartDateTime").text = time.ctime(start_time)
    ET.SubElement(build, "StartBuildTime").text = str(start_time)
    ET.SubElement(build, "BuildCommand").text = args.build_command
    
    # Warnings
    if args.warning:
        for i, issue_str in enumerate(args.warning):
            data = parse_build_issue(issue_str, args.separator, i)
            warning = ET.SubElement(build, "Warning")
            ET.SubElement(warning, "BuildLogLine").text = data['BuildLogLine']
            ET.SubElement(warning, "Text").text = data['Text']
            ET.SubElement(warning, "SourceFile").text = data['SourceFile']
            ET.SubElement(warning, "SourceLineNumber").text = data['SourceLineNumber']
            ET.SubElement(warning, "PreContext").text = data['PreContext']
            ET.SubElement(warning, "PostContext").text = data['PostContext']
            ET.SubElement(warning, "RepeatCount").text = data['RepeatCount']

    # Errors
    if args.error:
        for i, issue_str in enumerate(args.error):
            data = parse_build_issue(issue_str, args.separator, i)
            error = ET.SubElement(build, "Error")
            ET.SubElement(error, "BuildLogLine").text = data['BuildLogLine']
            ET.SubElement(error, "Text").text = data['Text']
            ET.SubElement(error, "SourceFile").text = data['SourceFile']
            ET.SubElement(error, "SourceLineNumber").text = data['SourceLineNumber']
            ET.SubElement(error, "PreContext").text = data['PreContext']
            ET.SubElement(error, "PostContext").text = data['PostContext']
            ET.SubElement(error, "RepeatCount").text = data['RepeatCount']

    ET.SubElement(build, "Log", Encoding="base64", Compression="bin/gzip")
    
    end_time = int(time.time())
    ET.SubElement(build, "EndDateTime").text = time.ctime(end_time)
    ET.SubElement(build, "EndBuildTime").text = str(end_time)
    ET.SubElement(build, "ElapsedMinutes").text = "0"

    xmlstr = minidom.parseString(ET.tostring(site)).toprettyxml(indent="\t")
    
    with open(args.output, "w") as f:
        f.write(xmlstr)
    
    print(f"Generated {args.output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Build.xml for CDash")
    parser.add_argument("--build-name", required=True, help="Name of the build")
    parser.add_argument("--build-stamp", required=True, help="Build stamp")
    parser.add_argument("--site-name", required=True, help="Name of the site")
    parser.add_argument("--build-command", default="make", help="Build command")
    parser.add_argument("--warning", action='append', help="Warning info (Text:SourceFile:Line:LogLine:Pre:Post:Repeat). Use --separator to change delimiter.")
    parser.add_argument("--error", action='append', help="Error info (Text:SourceFile:Line:LogLine:Pre:Post:Repeat). Use --separator to change delimiter.")
    parser.add_argument("--separator", default=":", help="Separator for info (default: ':'). Supports escaping.")
    parser.add_argument("--output", default="Build.xml", help="Output filename")
    
    args = parser.parse_args()
    generate_build_xml(args)
