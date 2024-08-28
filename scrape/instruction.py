

def Response(status:bool, message:str, version = "N/A", path = "N/A") -> dict[str,str,str,str]:
    """ Return a response dictionary with status, message, version, and path.
    
    :param status: Boolean status of the response
    :param message: Message describing the response
    :param version: Version string (default: 'N/A')
    :param path: Path string (default: 'N/A')
    
    :return: Dictionary containing status, message, version, and path
    """
    return {
        "status": status,
        "message": message,
        "version": version,
        "path": path
    }
    
    
def compare_versions(version1: str, version2: str) -> int:
    """
    Compare two version strings.
    
    :param version1: First version string (e.g., '1.2.3')
    :param version2: Second version string (e.g., '1.2.4')
    :return: -1 if version1 < version2, 1 if version1 > version2, 0 if equal
    """
    def split_version(version: str) -> list[int]:
        # Split the version by '.' and convert each part to an integer
        return [int(part) for part in version.split('.')]

    v1_parts = split_version(version1)
    v2_parts = split_version(version2)

    # Compare each part of the version
    for v1, v2 in zip(v1_parts, v2_parts):
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1
    
    # If all parts are equal but lengths differ (e.g., '1.0' vs '1.0.1')
    if len(v1_parts) < len(v2_parts):
        return -1
    elif len(v1_parts) > len(v2_parts):
        return 1

    return 0 # All parts are equal
    

def compare_app_version(current_version:str, requirements:dict,app_name) -> dict:
    try:
        version = current_version
        
        if requirements['target'] == None and requirements['minimum'] == None:
            return Response(True, "No requirements specified for {app_name}")
        
        if requirements['target'] != None:
            if compare_versions(version, requirements['target']) != 0:
                return Response(False, f"{app_name} version {version} does not match target version {requirements['target']}")
            
        if requirements['minimum'] != None:
            if compare_versions(version, requirements['minimum']) == -1:
                return Response(False, f"{app_name} version {version} is less than minimum version {requirements['minimum']}")
            
        return Response(True, f"{app_name} version {version} meets all requirements")
    
        
    except Exception as e:
        return Response(False, str(e))
    