import time

class PCB:
    #Bloque de Control de Procesos (PCB).Representa la estructura de datos de un proceso dentro del sistema operativo.
    def __init__(self, pid, tamano_memoria, rafaga_total):
        #Inicializa un nuevo proceso con sus atributos fundamentales.
        self.pid = pid #Identificador unico del proceso.
        self.estado = "Listo"  # Estados posibles: Listo, Ejecucion, Espera, Terminado
        self.tamano_memoria = tamano_memoria #Espacio que cocupa en la memeoria ram
        self.rafaga_total = rafaga_total #Tiempo total de CPU que el proceso necesita
        self.rafaga_restante = rafaga_total # Al inicio, la rafaga restante es igual a la total

    def __str__(self):
        #Se usa para imprimir la informacion del proceso facilmente en consola.
        return f"PID: {self.pid} | Estado: {self.estado} | RAM: {self.tamano_memoria}MB | Rafaga: {self.rafaga_restante}/{self.rafaga_total}"

# VARIABLES GLOBALES DEL SISTEMA

MEMORIA_MAXIMA = 100  # Limite estricto de memoria fisica en MB
memoria_disponible = MEMORIA_MAXIMA  # Rastrea cuanta memoria queda libre
cola_listos = []  # Lista que actuara como cola de procesos para el Round Robin
contador_pid = 1
QUANTUM = 3

# Variables para el Semáforo (Opción 3)
semaforo_ocupado = False
proceso_en_seccion_critica = None
cola_espera_semaforo = []
variable_compartida = 0 # Esta es la región simulada

# Variables para Deadlock (Opción 4)
recurso1_asignado_a = None
recurso2_asignado_a = None

# Variables para el Modo de Simulación
modo_seguro = True  # Seguro COn Control y Sin Control Carrera

# Variables para Semáforo Contador (Estacionamiento)
MAX_ESPACIOS = 5
espacios_disponibles = MAX_ESPACIOS
estacionamiento = []  # Hilos ocupando un espacio
cola_espera_estacionamiento = [] # Hilos bloqueados
log_eventos = []
contador_hilos = 0

# Variables para el Monitor (Cuenta Bancaria)
SALDO_INICIAL = 1000
saldo_bancario = SALDO_INICIAL
log_eventos_monitor = []
hilos_esperando_retiro = 0  # Simula la cola de la variable de condición
contador_hilos_monitor = 0

# Variables para Paso de Mensajes (Sistema de Pedidos)
MAX_MENSAJES = 5
cola_mensajes = []
registro_mensajes = []
contador_pedidos = 100 # Para iniciar en Pedido #101

def menu_principal():
    """
    Despliega el menu interactivo por linea de comandos (CLI).
    Mantiene el programa en ejecucion mediante un bucle y permite al usuario 
    interactuar con los diferentes modulos del simulador.
    """
    global memoria_disponible, contador_pid, semaforo_ocupado, proceso_en_seccion_critica, variable_compartida, recurso1_asignado_a, recurso2_asignado_a, modo_seguro, espacios_disponibles, estacionamiento, cola_espera_estacionamiento, log_eventos, contador_hilos, saldo_bancario, log_eventos_monitor, hilos_esperando_retiro, contador_hilos_monitor, cola_mensajes, registro_mensajes, contador_pedidos
    contador_pid = 1 # Variable para asignar identificadores unicos autoincrementables

    while True:
        # Encabezado del menu y estado actual del sistema
        print("\n" + "="*35)
        print("   SIMULADOR DE KERNEL - CLI")
        print("="*35)
        # Mostrar el modo actual
        modo_str = "CON CONTROL (SEGURO)" if modo_seguro else "SIN CONTROL (CARRERA)"
        print(f"Modo Actual: {modo_str}")
        print(f"RAM Disponible: {memoria_disponible} MB / {MEMORIA_MAXIMA} MB")
        print(f"Procesos en Cola de Listos: {len(cola_listos)}")
        print("-" * 35)
        
        #opciones disponibles
        print("0. Cambiar Modo de Simulacion")
        print("1. Crear nuevo proceso (Validacion RAM)")
        print("2. Ejecutar Planificador (Round Robin)")
        print("3. Simular Concurrencia")
        print("4. Simular Interbloqueo (Deadlock)")
        print("--- EXTRAS (Mecanismos Avanzados de Concurrencia) ---")
        print("5. Simular Semaforo Contador (Estacionamiento)")
        print("6. Simular Monitor (Cuenta Bancaria)")
        print("7. Simular Paso de Mensajes (Sistema de Pedidos)")
        print("-----------------------------------------------------")
        print("8. Salir")
        
        opcion = input("\nSeleccione una opcion: ")
        # OPCION 0: CAMBIA ENTRE MODO SEGURO Y SIN CONTROL
        if opcion == "0":
            modo_seguro = not modo_seguro
            nuevo_modo = "Con Control (Seguro)" if modo_seguro else "Sin Control (Carrera)"
            print(f"\n[INFO] Modo cambiado a: {nuevo_modo}")

        # OPCION 1: CREAR PROCESO Y VALIDAR MEMORIA
        elif opcion == "1":
            print("\n--- CREAR NUEVO PROCESO ---")
            try:
                tamano = int(input("Ingrese el tamano en memoria (MB): "))
                rafaga = int(input("Ingrese la rafaga de CPU total requerida: "))
                
                # Validacion de asignacion de memoria
                if tamano > memoria_disponible:
                    # Se rechaza el proceso si supera la memoria disponible
                    print(f"\n[ERROR] Out of Memory. El proceso requiere {tamano} MB, pero solo hay {memoria_disponible} MB disponibles.")
                    print("Proceso rechazado.")
                else:
                    # Si hay espacio suficiente se crea el proceso y se asigna la memoria
                    nuevo_proceso = PCB(contador_pid, tamano, rafaga)
                    cola_listos.append(nuevo_proceso)
                    memoria_disponible -= tamano  # Se resta el espacio ocupado
                    
                    print(f"\n[EXITO] Proceso creado y cargado en memoria:")
                    print(nuevo_proceso)
                    contador_pid += 1  # ID autoincrementable para el siguiente proceso

            except ValueError:
                print("\n[ERROR] Entrada invalida. Por favor, ingrese unicamente numeros enteros.")
                
        #OPCION 2: EJECUCION DE PLANIFICADOR CON ROUND ROBIN 
        elif opcion == "2":
            print("\n--- EJECUCION DE PLANIFICADOR (ROUND ROBIN) ---")
            if not cola_listos:
                print("No hay procesos en la cola de listos para ejecutar.")
            else:
                print(f"Iniciando simulacion con Quantum = {QUANTUM}...")
                
                # Ciclo que se ejecuta hasta vaciar la cola de listos
                while cola_listos:
                    # Se extrae el primer proceso de la cola
                    proceso_actual = cola_listos.pop(0)
                    proceso_actual.estado = "Ejecucion"
                    
                    print(f"\n[CPU] Atendiendo PID: {proceso_actual.pid} | Rafaga inicial en este turno: {proceso_actual.rafaga_restante}")
                    time.sleep(1) # Pausa de 1 segundo para simular procesamiento
                    
                    # Determinar el tiempo a ejecutar en este turno
                    if proceso_actual.rafaga_restante > QUANTUM:
                        tiempo_ejecucion = QUANTUM
                    else:
                        tiempo_ejecucion = proceso_actual.rafaga_restante
                        
                    # Restar el tiempo ejecutado a la ráfaga del proceso
                    proceso_actual.rafaga_restante -= tiempo_ejecucion
                    
                    # Validar si el proceso terminó o si vuelve a la cola
                    if proceso_actual.rafaga_restante > 0:
                        proceso_actual.estado = "Listo"
                        print(f"[-] Cambio de contexto. El PID {proceso_actual.pid} agoto su quantum y regresa a la cola.")
                        cola_listos.append(proceso_actual)
                    else:
                        proceso_actual.estado = "Terminado"
                        memoria_disponible += proceso_actual.tamano_memoria # Liberar RAM
                        print(f"[+] Proceso PID {proceso_actual.pid} TERMINADO. Se liberaron {proceso_actual.tamano_memoria}MB de RAM.")
                
                print("\nPlanificacion finalizada. Cola de listos vacia.")
    
        # OPCION 3: CONCURRENCIA
        elif opcion == "3":
            print("\n--- SIMULACION DE CONCURRENCIA ---")
            
            # SE muestra el modo sin control
            if not modo_seguro:
                print("\n[MODO: SIN CONTROL]")
                print("El sistema no tiene control. Se generara informacion incoherente.")
                print("Vuelve al menu principal y activa el modo 'Con Control (Seguro)' para habilitar las opciones de exclusión mutua.")
                
                if len(cola_listos) >= 2:
                    p1 = cola_listos[0]
                    p2 = cola_listos[1]
                    print(f"\nSimulando condicion de carrera entre PID {p1.pid} y PID {p2.pid} sobre 'variable_compartida'...")
                    # Simulación de lectura y escritura simultánea sin exclusión mutua
                    temp_v1 = variable_compartida
                    temp_v2 = variable_compartida
                    
                    print(f"-> PID {p1.pid} lee valor: {temp_v1}")
                    print(f"-> PID {p2.pid} lee valor: {temp_v2}")
                    # Valor fcictisio de 50
                    temp_v1 += 50
                    temp_v2 += 50
                    
                    # El último en escribir sobreescribe al anterior (colisión)
                    variable_compartida = temp_v2 
                    print(f"-> PID {p1.pid} intenta guardar {temp_v1}")
                    print(f"-> PID {p2.pid} guarda {temp_v2} (Sobrescribe)")
                    
                    print(f"\n[RESULTADO ERRONEO] Valor final de variable_compartida: {variable_compartida}")
                    print("El resultado dependio del orden de ejecucion. (Deberia haber sido mayor).")
                else:
                    print("\n[!] Necesitas al menos 2 procesos en Cola de Listos para simular la carrera.")
            
            else:
                # Se muestra el modo con control
                print("\n[MODO: CON CONTROL SINCRONIZADO]")
                print("Exclusion Mutua + Sincronizacion")
                print("Garantiza acceso atomico exclusivo a la vez y un orden de ejecucion coherente.")
                
                print(f"\nEstado del Semaforo: {'OCUPADO (Rojo)' if semaforo_ocupado else 'LIBRE (Verde)'}")
                if proceso_en_seccion_critica:
                    print(f"Proceso en Seccion Critica: PID {proceso_en_seccion_critica.pid}")
                print(f"Procesos en Cola de Espera: {len(cola_espera_semaforo)}")
                print(f"Valor Variable Compartida: {variable_compartida}")
                
                print("\nSubmenu:")
                print("a) Ejecutar wait() -> Un proceso de Cola Listos intenta entrar")
                print("b) Ejecutar signal() -> El proceso actual libera la seccion")
                sub_op = input("Seleccione (a/b): ").lower()
                
                if sub_op == 'a':
                    if not cola_listos:
                        print("[!] No hay procesos en Cola de Listos. Crea uno en la Opcion 1 primero.")
                    else:
                        proc = cola_listos.pop(0) 
                        print(f"\n-> El PID {proc.pid} ejecuta wait()...")
                        
                        if not semaforo_ocupado:
                            semaforo_ocupado = True
                            proceso_en_seccion_critica = proc
                            proc.estado = "Seccion Critica"
                            variable_compartida += 50 # Se suma 50 como en el modo sin control
                            print(f"[EXITO] El PID {proc.pid} ha entrado a la Seccion Critica de forma segura.")
                        else:
                            proc.estado = "Espera"
                            cola_espera_semaforo.append(proc)
                            print(f"[BLOQUEO] Semaforo ocupado. El PID {proc.pid} se va a la cola de espera para evitar colisiones.")
                            
                elif sub_op == 'b':
                    if semaforo_ocupado and proceso_en_seccion_critica:
                        print(f"\n-> El PID {proceso_en_seccion_critica.pid} ejecuta signal()...")
                        
                        proceso_en_seccion_critica.estado = "Listo"
                        cola_listos.append(proceso_en_seccion_critica)
                        print(f"[LIBERADO] El PID {proceso_en_seccion_critica.pid} salio de la Seccion Critica.")
                        
                        proceso_en_seccion_critica = None
                        semaforo_ocupado = False
                        
                        if cola_espera_semaforo:
                            siguiente = cola_espera_semaforo.pop(0)
                            semaforo_ocupado = True
                            proceso_en_seccion_critica = siguiente
                            siguiente.estado = "Seccion Critica"
                            variable_compartida += 50 # Se suma 50 del proceso en espera
                            print(f"[DESPERTAR] El PID {siguiente.pid} sale de espera y entra a la Seccion Critica.")
                    else:
                        print("\n[!] No hay ningun proceso en la Seccion Critica para liberar.")
                else:
                    print("\n[Error] Opcion invalida.")
            
         # OPCION 4: DEADLOCK   
        elif opcion == "4":
            print("\n--- SIMULACION DE INTERBLOQUEO (DEADLOCK) ---")
            
            # Se necesitan al menos 2 procesos para simular el interbloqueo
            if len(cola_listos) < 2:
                print("[!] Para simular el Deadlock se necesitan al menos 2 procesos en la Cola de Listos.")
                print("Por favor, ve a la Opcion 1 y crea procesos suficientes.")
            else:
                proceso_a = cola_listos[0]
                proceso_b = cola_listos[1]
                
                print(f"\nForzando condicion de espera circular entre PID {proceso_a.pid} y PID {proceso_b.pid}...")
                time.sleep(1)
                
                # 1 Asignación inicial de recursos
                recurso1_asignado_a = proceso_a
                recurso2_asignado_a = proceso_b
                print(f"-> Recurso 1 asignado y retenido por el PID {proceso_a.pid}")
                print(f"-> Recurso 2 asignado y retenido por el PID {proceso_b.pid}")
                time.sleep(1)
                
                # 2 Solicitud cruzada (Causa del Deadlock)
                print(f"\n-> PID {proceso_a.pid} solicita Recurso 2 (Ocupado por PID {proceso_b.pid})")
                print(f"-> PID {proceso_b.pid} solicita Recurso 1 (Ocupado por PID {proceso_a.pid})")
                time.sleep(1)
                
                # 3 Detección
                print("\n[ALERTA ROJA] ¡DEADLOCK DETECTADO! Condicion de espera circular confirmada.")
                print("Ambos procesos estan bloqueados mutuamente de forma indefinida.")
                
                # 4 Resolución
                print("\nOpciones de Resolucion del Deadlock:")
                print(f"1. Abortar Proceso A (PID {proceso_a.pid})")
                print(f"2. Abortar Proceso B (PID {proceso_b.pid})")
                print("3. No hacer nada (Mantener Deadlock)")
                
                res = input("Seleccione el proceso a abortar forzosamente (1/2): ")
                
                if res == "1":
                    print(f"\n[RESOLUCION] Abortando forzosamente el Proceso A (PID {proceso_a.pid})...")
                    cola_listos.remove(proceso_a)
                    memoria_disponible += proceso_a.tamano_memoria # Se libera su memoria RAM
                    recurso1_asignado_a = proceso_b # El recurso 1 se le entrega al proceso B
                    print(f"-> Se liberaron los recursos del PID {proceso_a.pid}.")
                    print(f"[EXITO] El PID {proceso_b.pid} ahora posee el Recurso 1 y el Recurso 2. Deadlock resuelto.")
                elif res == "2":
                    print(f"\n[RESOLUCION] Abortando forzosamente el Proceso B (PID {proceso_b.pid})...")
                    cola_listos.remove(proceso_b)
                    memoria_disponible += proceso_b.tamano_memoria # Se libera su memoria RAM
                    recurso2_asignado_a = proceso_a # El recurso 2 se le entrega al proceso A
                    print(f"-> Se liberaron los recursos del PID {proceso_b.pid}.")
                    print(f"[EXITO] El PID {proceso_a.pid} ahora posee el Recurso 1 y el Recurso 2. Deadlock resuelto.")
                else:
                    print("\n[!] No se tomo accion. Los procesos siguen bloqueados.")
                
                # Limpieza de variables para permitir futuras simulaciones limpias
                recurso1_asignado_a = None
                recurso2_asignado_a = None
                
        # OPCION 5: SEMAFORO CONTADOR (ESTACIONAMIENTO)
        elif opcion == "5":
            while True:
                # Renderizado visual del estado actual del estacionamiento y cola de espera
                print("\n" + "="*50)
                print("   INTERACCION DE MECANISMOS - SEMAFOROS")
                print("="*50)
                print(f"Estacionamiento (Capacidad Maxima = {MAX_ESPACIOS})")
                print(f"Espacios Disponibles (Contador S): {espacios_disponibles}")
                print(f"Ocupantes actuales: {estacionamiento if estacionamiento else 'Ninguno'}")
                print("-" * 50)
                
                print(f"Cola de Espera (Queue): {len(cola_espera_estacionamiento)} hilos esperando")
                if cola_espera_estacionamiento:
                    print(f"Bloqueados: {cola_espera_estacionamiento}")
                else:
                    print("Ningun hilo bloqueado en espera...")
                print("-" * 50)
                # Despliegue de la bitacora de auditoria (Log de eventos)
                print("LOG DE EVENTOS:")
                if not log_eventos:
                    print("  (Vacio)")
                else:
                    # Mostrar los últimos 5 eventos para no saturar la pantalla
                    for evento in log_eventos[-5:]:
                        print(f"  > {evento}")
                
                print("\nACCIONES DEL SEMAFORO:")
                print(" a) Solicitar Espacio (wait / P)")
                print(" b) Liberar Espacio (signal / V)")
                print(" c) Reiniciar Estacionamiento")
                print(" q) Volver al Menu Principal")
                
                accion = input("\nSeleccione accion: ").lower()
                
                timestamp = time.strftime("[%H:%M:%S]")
                # OPERACION WAIT() / P(), decrementa el contador del semaforo si hay disponibilidad. 
                # Si el contador es 0, bloquea e inserta el hilo en la cola de espera.
                if accion == 'a':
                    contador_hilos += 1
                    nuevo_hilo = f"Hilo #{contador_hilos}"
                    log_eventos.append(f"{timestamp} {nuevo_hilo} ejecuta wait()/P()...")
                    
                    if espacios_disponibles > 0:
                        espacios_disponibles -= 1
                        estacionamiento.append(nuevo_hilo)
                        log_eventos.append(f"{timestamp} ! Espacio asignado. {nuevo_hilo} entra al estacionamiento.")
                    else:
                        cola_espera_estacionamiento.append(nuevo_hilo)
                        log_eventos.append(f"{timestamp} ! Contador S = 0. {nuevo_hilo} entra a la Cola de Espera (Bloqueado).")
                # OPERACION SIGNAL() / V(), incrementa el contador del semaforo o transfiere el acceso directamente a un hilo que se encuentre bloqueado en la cola de espera (FIFO).   
                elif accion == 'b':
                    if estacionamiento:
                        hilo_saliente = estacionamiento.pop(0)
                        log_eventos.append(f"{timestamp} {hilo_saliente} ejecuta signal()/V()...")
                        # Si existen hilos esperando, se le otorga la vacante sin incrementar el contador libre
                        if cola_espera_estacionamiento:
                            hilo_despertado = cola_espera_estacionamiento.pop(0)
                            estacionamiento.append(hilo_despertado)
                            log_eventos.append(f"{timestamp} ! Espacio transferido. {hilo_despertado} sale de espera y ocupa el lugar.")
                        else:
                            espacios_disponibles += 1
                            log_eventos.append(f"{timestamp} ! Espacio liberado por {hilo_saliente}. Contador S = {espacios_disponibles}.")
                    else:
                        log_eventos.append(f"{timestamp} [Error] El estacionamiento ya esta vacio. No se puede ejecutar signal().")
                # Restablece la estructura del semaforo a su estado inicial.        
                elif accion == 'c':
                    espacios_disponibles = MAX_ESPACIOS
                    estacionamiento.clear()
                    cola_espera_estacionamiento.clear()
                    log_eventos.clear()
                    contador_hilos = 0
                    log_eventos.append(f"{timestamp} Sistema reiniciado por el usuario.")
                    
                elif accion == 'q':
                    break
                else:
                    print("Opcion invalida.")  

        # OPCION 6: MONITOR (CUENTA BANCARIA)
        elif opcion == "6":
            while True:
                # Interfaz del Monitor de la Cuenta Bancaria
                print("\n" + "="*50)
                print("   INTERACCION DE MECANISMOS - MONITORES")
                print("="*50)
                print(f"Cuenta Bancaria | Saldo Actual: Q{saldo_bancario}")
                print(f"Hilos en espera de retiro grande (Q1500): {hilos_esperando_retiro}")
                print("-" * 50)
                # Bitacora de eventos del Monitor
                print("LOG DE EVENTOS:")
                if not log_eventos_monitor:
                    print("  (Vacio)")
                else:
                    for evento in log_eventos_monitor[-6:]:
                        print(f"  > {evento}")
                
                print("\nMETODOS DEL MONITOR:")
                print(" a) Depositar Q100")
                print(" b) Retirar Q50")
                print(" c) Intentar Retiro Grande (Q1500)")
                print(" d) Reiniciar Monitor")
                print(" q) Volver al Menu Principal")
                
                accion = input("\nSeleccione accion: ").lower()
                timestamp = time.strftime("[%H:%M:%S]")
                # METODO DEPOSITAR() CON NOTIFY() AUTOMATICO
                if accion == 'a':
                    contador_hilos_monitor += 1
                    hilo = f"Hilo M#{contador_hilos_monitor}"
                    saldo_bancario += 100
                    log_eventos_monitor.append(f"{timestamp} {hilo} ejecuta depositar(100). Saldo: Q{saldo_bancario}")
                    
                    # Simulación del notify() de la variable de condición
                    if hilos_esperando_retiro > 0 and saldo_bancario >= 1500:
                        hilos_esperando_retiro -= 1
                        saldo_bancario -= 1500
                        log_eventos_monitor.append(f"{timestamp} ! notify() activado. Un hilo en espera despierta y retira Q1500. Saldo restante: Q{saldo_bancario}")
                # METODO RETIRAR()
                elif accion == 'b':
                    contador_hilos_monitor += 1
                    hilo = f"Hilo M#{contador_hilos_monitor}"
                    if saldo_bancario >= 50:
                        saldo_bancario -= 50
                        log_eventos_monitor.append(f"{timestamp} {hilo} ejecuta retirar(50). Saldo: Q{saldo_bancario}")
                    else:
                        log_eventos_monitor.append(f"{timestamp} [Error] {hilo} intento retirar 50 pero no hay fondos suficientes.")
                # METODO RETIRAR() CONDICIONAL CON WAIT()     
                elif accion == 'c':
                    contador_hilos_monitor += 1
                    hilo = f"Hilo M#{contador_hilos_monitor}"
                    if saldo_bancario >= 1500:
                        saldo_bancario -= 1500
                        log_eventos_monitor.append(f"{timestamp} {hilo} ejecuta retiro grande exitoso (1500). Saldo: Q{saldo_bancario}")
                    else:
                        # SIMULACION DEL WAIT(): Registro de suspension de hilo en la variable de condicion
                        hilos_esperando_retiro += 1
                        log_eventos_monitor.append(f"{timestamp} {hilo} intenta retirar 1500. Fondos insuficientes. Ejecuta wait() y se bloquea.")
                # Reinicio del estado del moniotr        
                elif accion == 'd':
                    saldo_bancario = SALDO_INICIAL
                    log_eventos_monitor.clear()
                    hilos_esperando_retiro = 0
                    contador_hilos_monitor = 0
                    log_eventos_monitor.append(f"{timestamp} Monitor reiniciado a saldo inicial.")
                    
                elif accion == 'q':
                    break
                else:
                    print("Opcion invalida.")  
    
        # OPCION 7: PASO DE MENSAJES (SISTEMA DE PEDIDOS)
        elif opcion == "7":
            while True:
                # Interfaz del canal de comunicacion por paso de mensajes
                print("\n" + "="*50)
                print("   INTERACCION DE MECANISMOS - PASO DE MENSAJES")
                print("="*50)
                print("EJEMPLO REAL: SISTEMA DE PROCESAMIENTO DE PEDIDOS")
                print(f"Cola de Mensajes: {len(cola_mensajes)} / {MAX_MENSAJES} msgs")
                
                if cola_mensajes:
                    print(f"Mensajes en tránsito: {cola_mensajes}")
                else:
                    print("Mensajes en tránsito: [ Cola vacía ]")
                print("-" * 50)
                # Bitacora de auditoria del intercambio de mensajes
                print("REGISTRO DE INTERCAMBIO DE MENSAJES:")
                if not registro_mensajes:
                    print("  (Vacio)")
                else:
                    for evento in registro_mensajes[-6:]:
                        print(f"  > {evento}")
                
                print("\nACCIONES DISPONIBLES:")
                print(" a) 1. Pedido (Cliente) - send('Pedido #XXX')")
                print(" b) 2 & 3. Inventario y Pago - receive() & Process")
                print(" c) Limpiar Registro / Reiniciar")
                print(" q) Volver al Menu Principal")
                
                accion = input("\nSeleccione accion: ").lower()
                timestamp = time.strftime("[%H:%M:%S]")
                # PRIMITIVA SEND() (PROCESO PRODUCTOR / CLIENTE)
                if accion == 'a':
                    if len(cola_mensajes) < MAX_MENSAJES:
                        contador_pedidos += 1
                        nuevo_pedido = f"Pedido #{contador_pedidos}"
                        cola_mensajes.append(nuevo_pedido)
                        registro_mensajes.append(f"{timestamp} [Proceso A] Genera orden de compra y envia {nuevo_pedido} a la cola.")
                    else:
                        registro_mensajes.append(f"{timestamp} [Error] Cola llena (5/5). El Proceso A debe esperar a que se procesen pedidos.")
                # PRIMITIVA RECEIVE() (PROCESO CONSUMIDOR / INVENTARIO Y PAGO)
                elif accion == 'b':
                    if cola_mensajes:
                        # FIFO: El primero en entrar es el primero en salir (pop(0))
                        pedido_procesado = cola_mensajes.pop(0)
                        registro_mensajes.append(f"{timestamp} [Procesos B y C] receive(). Consume {pedido_procesado}...")
                        registro_mensajes.append(f"{timestamp} -> Verifica stock y procesa cobros de {pedido_procesado} con éxito.")
                    else:
                        registro_mensajes.append(f"{timestamp} [En espera] No hay mensajes. Inventario/Pago bloqueado en receive().")
                # Reinicio de pasos de mensaje        
                elif accion == 'c':
                    cola_mensajes.clear()
                    registro_mensajes.clear()
                    contador_pedidos = 100
                    registro_mensajes.append(f"{timestamp} Cola y registros limpiados por el usuario.")
                    
                elif accion == 'q':
                    break
                else:
                    print("Opcion invalida.")                            
        elif opcion == "8":
            print("\nApagando simulador...")
            break
        else:
            print("\n[Error] Opcion no valida. Intente de nuevo.")

if __name__ == "__main__":
    menu_principal()