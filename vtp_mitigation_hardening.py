#!/usr/bin/env python3
"""
MÓDULO DE DEFENSA: Hardening de Capa 2 y Políticas de Mitigación VTP
Ruta recomendada: /hardening/vtp_mitigation_hardening.py
"""

from netmiko import ConnectHandler, NetmikoAuthenticationException, NetmikoTimeoutException

# Parámetros de conexión para el Switch de Producción (Víctima potencial)
SW_LEGITIMO_PERFIL = {
    "device_type": "cisco_ios",
    "host": "202.121.66.12",  # Dirección IP de SW-2 (Cliente) o SW-1 (Servidor)
    "username": "admin",
    "password": "PasswordLaboratorio123",
    "secret": "PasswordLaboratorio123",
}

# Directivas de seguridad para mitigar ataques VTP y vulnerabilidades de DTP
COMANDOS_HARDENING = [
    # 1. Aplicación de firma criptográfica MD5 al dominio
    "vtp password ClaveUltraSeguraITLA",
    
    # 2. Hardening del enlace troncal legítimo
    "interface ethernet 0/0",
    "description => Enlace Troncal Seguro Inter-Switch <=",
    "switchport trunk encapsulation dot1q",
    "switchport mode trunk",
    "switchport nonegotiate",          # Detiene la negociación dinámica DTP
    "switchport trunk native vlan 99",  # Mitigación contra VLAN Hopping
    "exit",
    
    # 3. Hardening del perímetro de acceso (Usuarios finales)
    "interface ethernet 0/1",
    "description => Puerto de Acceso Asegurado - Solo Terminales de Usuario <=",
    "switchport mode access",
    "switchport access vlan 10",
    "switchport nonegotiate",          # Impide que un atacante convierta este puerto en trunk
    "spanning-tree portfast",          # Convergencia inmediata
    "spanning-tree bpduguard enable"   # Bloquea el puerto si detecta un switch intruso
]

def aplicar_hardening():
    print(f"[*] Conectando al Switch de Infraestructura ({SW_LEGITIMO_PERFIL['host']}) para aplicar Hardening...")
    try:
        with ConnectHandler(**SW_LEGITIMO_PERFIL) as net_connect:
            net_connect.enable()
            print("[*] Aplicando políticas defensivas de Capa 2...")
            
            output = net_connect.send_config_set(COMANDOS_HARDENING)
            print(output)
            
            net_connect.send_command("write memory")
            print("[+] Inmunización completada. Extrayendo telemetría de verificación...\n")
            
            # Verificación en caliente post-hardening
            vtp_status = net_connect.send_command("show vtp status")
            print("--- [ESTADO VTP ACTUALIZADO] ---")
            print(vtp_status)
            
    except (NetmikoTimeoutException, NetmikoAuthenticationException) as e:
        print(f"[-] Error crítico al conectar con el Switch de Producción: {e}")

if __name__ == "__main__":
    aplicar_hardening()