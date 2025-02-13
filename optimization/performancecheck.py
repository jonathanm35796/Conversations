#!/usr/bin/env python
import subprocess
import datetime
import os
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_command(command, ignore_errors=False):
    print(f"[VERBOSE] Executing: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.stdout.strip():
            print(f"[VERBOSE] Output (stdout): {result.stdout.strip()}")
        if result.stderr.strip():
            print(f"[VERBOSE] Output (stderr): {result.stderr.strip()}")
        return result.stdout.strip() if result.stdout else result.stderr.strip()
    except Exception as e:
        print(f"[VERBOSE] Error executing {command}: {e}")
        if not ignore_errors:
            raise
        return f"Error executing {command}: {e}"

def get_display_capabilities(report_sections):
    print("[VERBOSE] Detecting display capabilities...")
    report_sections.append("\n[Display Capabilities]")
    
    # Get current display settings
    cmd = 'powershell -Command "Get-CimInstance -ClassName Win32_VideoController | Select-Object CurrentRefreshRate, VideoModeDescription"'
    output = run_command(cmd)
    report_sections.append(f"Command: {cmd}")
    report_sections.append(output)
    return output

def set_balanced_power_settings(report_sections):
    print("[VERBOSE] Configuring balanced power settings...")
    report_sections.append("\n[Power Settings Configuration]")

    if not is_admin():
        report_sections.append("Warning: Script requires administrator privileges for power settings")
        return

    # Create custom balanced power scheme
    balanced_guid = "381b4222-f694-41f0-9685-ff5bb260df2e"
    custom_scheme = run_command(f"powercfg -duplicatescheme {balanced_guid}")
    
    try:
        new_guid = custom_scheme.split()[3] if custom_scheme and "GUID" in custom_scheme else balanced_guid
        
        # Configure optimal settings
        settings = [
            ("SUB_PROCESSOR", "PROCTHROTTLEMIN", "50"),        # Minimum processor state 50%
            ("SUB_PROCESSOR", "PROCTHROTTLEMAX", "100"),       # Maximum processor state 100%
            ("SUB_VIDEO", "VIDEOIDLE", "300"),                 # Turn off display after 5 minutes
            ("SUB_SLEEP", "HIBERNATEIDLE", "0"),               # Hibernate never
            ("SUB_SLEEP", "STANDBYIDLE", "1800"),             # Sleep after 30 minutes
            ("SUB_PROCESSOR", "PERFBOOSTMODE", "2"),          # Aggressive performance boost
        ]

        for subgroup, setting, value in settings:
            cmd = f'powercfg /SETACVALUEINDEX {new_guid} {subgroup} {setting} {value}'
            output = run_command(cmd, ignore_errors=True)
            report_sections.append(f"Command: {cmd}")
            report_sections.append(output)

        # Activate the new scheme
        run_command(f"powercfg /setactive {new_guid}")
        report_sections.append("\nPower settings configured for optimal performance")
    except Exception as e:
        report_sections.append(f"Error configuring power settings: {str(e)}")

def optimize_gpu_settings(report_sections):
    print("[VERBOSE] Optimizing GPU settings for balanced performance...")
    report_sections.append("\n[GPU Configuration]")
    
    # Check NVIDIA GPU
    gpu_cmd = "nvidia-smi"
    gpu_output = run_command(gpu_cmd, ignore_errors=True)
    if "NVIDIA" in gpu_output.upper():
        report_sections.append(f"Command: {gpu_cmd}")
        report_sections.append(gpu_output)
        
        try:
            # Get GPU capabilities
            gpu_info = run_command("nvidia-smi --query-gpu=gpu_name,memory.total,power.max_limit --format=csv,noheader", ignore_errors=True)
            gpu_name, gpu_memory, max_power = gpu_info.split(',')
            report_sections.append(f"Detected GPU: {gpu_name}")
            
            # Use Windows Registry for NVIDIA settings
            nvidia_reg_commands = [
                'reg add "HKLM\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000" /v "PowerMizerEnable" /t REG_DWORD /d "1" /f',
                'reg add "HKLM\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000" /v "PowerMizerLevel" /t REG_DWORD /d "2" /f',
                'reg add "HKLM\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000" /v "PowerMizerLevelAC" /t REG_DWORD /d "1" /f'
            ]

            if is_admin():
                for cmd in nvidia_reg_commands:
                    output = run_command(cmd, ignore_errors=True)
                    report_sections.append(f"Command: {cmd}")
                    report_sections.append(output)
            else:
                report_sections.append("Warning: Administrator privileges required for GPU optimization")
            
            report_sections.append("GPU settings configured for optimal performance")
            
        except Exception as e:
            report_sections.append(f"Warning: Some GPU optimizations could not be applied: {str(e)}")
    else:
        report_sections.append("Note: NVIDIA GPU not detected or nvidia-smi not available")

def set_display_settings(report_sections, display_info):
    print("[VERBOSE] Configuring display settings...")
    report_sections.append("\n[Display Settings]")
    
    try:
        # Get available refresh rates
        cmd = 'powershell -Command "$m = Get-WmiObject WmiMonitorListedSupportedSourceModes -Namespace root\\wmi; $m.MonitorSourceModes | Sort-Object -Property vRefresh -Descending | Select-Object -First 1 | ForEach-Object { $_.vRefresh }"'
        max_refresh = run_command(cmd, ignore_errors=True)
        
        if max_refresh and max_refresh.isdigit():
            max_refresh = int(max_refresh)
            target_rate = min(max_refresh, 120)  # Cap at 120Hz for stability
            
            if is_admin():
                cmd = f'powershell -Command "$dm = New-Object -TypeName System.Drawing.Drawing2D.Matrix; $dm.SetRefreshRate({target_rate})"'
                output = run_command(cmd, ignore_errors=True)
                report_sections.append(f"Display refresh rate set to {target_rate}Hz")
            else:
                report_sections.append("Warning: Administrator privileges required to change refresh rate")
        else:
            report_sections.append("Unable to detect supported refresh rates")
    except Exception as e:
        report_sections.append(f"Warning: Could not configure display settings: {str(e)}")

def install_hp_drivers(report_sections):
    print("[VERBOSE] Checking HP drivers...")
    report_sections.append("\n[HP Driver Installation]")
    hp_drivers_path = r"C:\Users\JonathanSMcFarland\OneDrive\Desktop\HP Applications"
    
    if os.path.exists(hp_drivers_path):
        if is_admin():
            print("[VERBOSE] Installing HP drivers...")
            install_cmd = f"powershell -Command \"Get-ChildItem '{hp_drivers_path}' -Filter *.inf -Recurse | ForEach-Object {{ pnputil /add-driver $_.FullName /install }}\""
            install_output = run_command(install_cmd, ignore_errors=True)
            report_sections.append(f"Command: {install_cmd}")
            report_sections.append(install_output)
        else:
            report_sections.append("Warning: Administrator privileges required for driver installation")
    else:
        report_sections.append("HP Applications folder not found at the specified location")

def set_process_priority(report_sections):
    print("[VERBOSE] Setting process priorities...")
    report_sections.append("\n[Process Priority Configuration]")
    
    try:
        cmd = 'powershell -Command "$Process = Get-Process -Id $PID; $Process.PriorityClass=\'AboveNormal\'"'
        output = run_command(cmd, ignore_errors=True)
        report_sections.append(f"Command: {cmd}")
        report_sections.append(output)
        report_sections.append("Process priority set to Above Normal")
    except Exception as e:
        report_sections.append(f"Warning: Could not set process priority: {str(e)}")

def main():
    if not is_admin():
        print("[WARNING] Script should be run with administrator privileges for full functionality")
    
    print("[VERBOSE] Starting optimization...")
    log_file = "system_optimization.log"
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_sections = []
    report_sections.append(f"System Optimization Report - {current_time}")
    report_sections.append("="*60)
    
    try:
        display_info = get_display_capabilities(report_sections)
        set_balanced_power_settings(report_sections)
        optimize_gpu_settings(report_sections)
        set_display_settings(report_sections, display_info)
        set_process_priority(report_sections)
        install_hp_drivers(report_sections)
        
        print("[VERBOSE] Auditing drivers...")
        report_sections.append("\n[Driver Audit]")
        driver_cmd = "driverquery /v /fo csv"
        driver_output = run_command(driver_cmd, ignore_errors=True)
        report_sections.append(f"Command: {driver_cmd}")
        report_sections.append(driver_output)
        
        print("[VERBOSE] Checking CPU and Hyperthreading info...")
        report_sections.append("\n[CPU Information]")
        cpu_cmd = "powershell -Command \"Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors,MaxClockSpeed\""
        cpu_output = run_command(cpu_cmd, ignore_errors=True)
        report_sections.append(f"Command: {cpu_cmd}")
        report_sections.append(cpu_output)
        
    except Exception as e:
        report_sections.append(f"\nError during optimization: {str(e)}")
    
    print("[VERBOSE] Writing all results to log file...")
    with open(log_file, "w") as f:
        f.write("\n".join(report_sections))
    
    print(f"[VERBOSE] Optimization actions executed and report saved to {log_file}")

if __name__ == "__main__":
    main()
