from flask import Flask, render_template, request, redirect, url_for, Response
import sqlite3
from fpdf import FPDF

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/procesar_formulario', methods=['POST'])
def procesar_formulario():
    datos_formulario = request.form
    try:
        conn = sqlite3.connect('database/medic_app.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO usuarios (
                nombres, apellidos, edad, altura, peso, antecedentes_h_arterial,
                antecedentes_e_cardiovasculares, antecedentes_e_toxicos, antecedentes_e_cerebrovascular, antecedentes_diabetes, antecedentes_dislipidemias, antecedentes_e_renal,
                h_arterial, e_cardiovasculares, e_toxicos, e_cerebrovascular, diabetes, dislipidemias,
                e_renal, alcohol, cocaina, anfetaminas, cafeina, antidepresivos,
                descongestionantes, aines, anticonceptivos, consumo, d_cabeza, nerviosismo,
                sangrado, s_zumbido, mareo, v_borrosa, palpitaciones, cansancio, hinchazon
            ) VALUES (?, ?, ?, ?, ?, ?, 
            ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datos_formulario['nombres'], 
            datos_formulario['apellidos'],
            datos_formulario['edad'], 
            datos_formulario['altura'],
            datos_formulario['peso'],
            datos_formulario['antecedentes_h_arterial'],
            datos_formulario['antecedentes_e_cardiovasculares'],
            datos_formulario['antecedentes_e_toxicos'],
            datos_formulario['antecedentes_e_cerebrovascular'],
            datos_formulario['antecedentes_diabetes'],
            datos_formulario['antecedentes_dislipidemias'],
            datos_formulario['antecedentes_e_renal'],
            datos_formulario['h_arterial'], 
            datos_formulario['e_cardiovasculares'],
            datos_formulario['e_toxicos'], 
            datos_formulario['e_cerebrovascular'],
            datos_formulario['diabetes'], 
            datos_formulario['dislipidemias'],
            datos_formulario['e_renal'], 
            datos_formulario['alcohol'],
            datos_formulario['cocaina'], 
            datos_formulario['anfetaminas'],
            datos_formulario['cafeina'], 
            datos_formulario['antidepresivos'],
            datos_formulario['descongestionantes'], 
            datos_formulario['aines'],
            datos_formulario['anticonceptivos'], 
            datos_formulario['consumo'],
            datos_formulario['d_cabeza'], 
            datos_formulario['nerviosismo'],
            datos_formulario['sangrado'], 
            datos_formulario['s_zumbido'],
            datos_formulario['mareo'], 
            datos_formulario['v_borrosa'],
            datos_formulario['palpitaciones'], 
            datos_formulario['cansancio'],
            datos_formulario['hinchazon']
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('exito'))
    except Exception as e:
        print(e)
        return redirect(url_for('error'))

@app.route('/exito')
def exito():
    return render_template('exito.html')

@app.route('/download')
def download():
    conn = sqlite3.connect('database/medic_app.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM usuarios ORDER BY id DESC LIMIT 1''')
    datos = cursor.fetchall()
    pdf = FPDF()
    pdf.add_page()
    page_width = pdf.w - 2 * pdf.l_margin
    pdf.set_font('Times','B',14.0) 
    pdf.cell(page_width, 0.0, 'Medic-App: Informe de paciente', align='C')
    pdf.ln(10)
    pdf.set_font('Times','',10.0)
    for row in datos:
        pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, f"{row[1]} {row[2]}")
        pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, f"Edad {row[3]}, Altura {row[4]} m, Peso {row[5]} Kg")
    pdf.ln(1)
    th = pdf.font_size
    riesgo=0
    altura = 0
    peso = 0
    for row in datos:
        for j in range(37):
            if j == 4:
                altura = float(row[j]) 
            if j == 5:
                peso = float(row[j]) 
            if str(row[j+1]) == "Si":
                riesgo+=1
    imc = (peso)/(altura**2)
    imc_redondeado = round(imc, 1)
    if imc_redondeado >= 30:
        riesgo += 3
        nivel_riesgo = "Riesgo 3"
        estado_peso = "Obesidad"
        recomendacion = "Se recomienda consultar con un profesional de la salud."
    elif 25 <= imc_redondeado < 30:
        riesgo += 2
        nivel_riesgo = "Riesgo 2"
        estado_peso = "Sobrepeso"
        recomendacion = "Se recomienda mantener una dieta equilibrada y realizar ejercicio regularmente."
    elif 18.5 <= imc_redondeado < 25:
        nivel_riesgo = "Riesgo 1"
        estado_peso = "Peso saludable"
        recomendacion = "Se recomienda mantener hábitos saludables para preservar el peso."
    else:
        nivel_riesgo = "Riesgo 3"
        estado_peso = "Bajo peso"
        recomendacion = "Se recomienda consultar con un profesional de la salud para evaluar la dieta y el estilo de vida."
        riesgo += 3
    if riesgo >= 3:
        nivel_riesgo = "Riesgo 3"
    elif 1 <= riesgo <= 2:
        nivel_riesgo = "Riesgo 2"
    else:
        nivel_riesgo = "Riesgo 1"
    x = pdf.get_x()
    y = pdf.get_y()
    ancho_rectangulo = pdf.get_string_width(nivel_riesgo) + 6 
    pdf.set_fill_color(173, 216, 230)
    pdf.rect(x, y, ancho_rectangulo, 10, 'F')
    pdf.set_text_color(0, 0, 0)
    pdf.text(x + 3, y + 5, nivel_riesgo)
    pdf.ln(10)
    x = pdf.l_margin
    y = pdf.get_y()
    pdf.multi_cell(page_width - 2 * pdf.l_margin, 3, f"Estado de peso: {estado_peso}")
    pdf.ln(5)
    pdf.multi_cell(page_width - 2 * pdf.l_margin, 3, f"Recomendación: {recomendacion}")
    pdf.ln(2)
    pdf.set_font('Times','B',14.0)
    pdf.multi_cell(page_width - 2 * pdf.l_margin, 3, "Recomendaciones por diagnóstico, antecedentes o prácticas")
    a, b, c, d = 0, 0, 0, 0
    for row in datos:
        for j in range(38):
            if str(row[j]) == "Si":
                riesgo+=1
            if (j>=6 and j<=12) and (str(row[j]) == "Si"):
                if a<1:
                    pdf.ln(10)
                    pdf.set_font('Times','B',14.0) 
                    pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Diagnósticos - antecedentes")
                    pdf.ln(10)
                a+=1
            pdf.set_font('Times','',10.0)
            if j == 6 and str(row[6]) == "Si":
                pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Hipertensión arterial: Reduce el exceso de peso y cuida la cintura. ... Haz ejercicio regularmente. ... Lleva una dieta saludable. ... Reduce la sal (sodio) en tu alimentación. ... Limita el consumo de alcohol. ... Dejar de fumar. ... Descansa bien durante la noche.")
            if j == 7 and str(row[7]) == "Si":
                pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Enfermedades Cardiovasculares. No fumes ni consumas tabaco. ... Muévete: intenta hacer al menos de 30 a 60 minutos de actividad al día. ... una dieta saludable para el corazón. ... mantener un peso saludable. ... Sueño de buena calidad. ... Controla el estrés. ... Preséntate a exámenes médicos regulares.")
            if j == 8 and str(row[8]) == "Si":
                pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Exposición a tóxicos. Retira todo lo que quede en la boca de la persona. Si sospechas que la sustancia tóxica es un producto de limpieza de uso doméstico u otra sustancia química, lee la etiqueta del recipiente y sigue las instrucciones para casos de intoxicación involuntaria.")
            if j == 9 and str(row[9]) == "Si":
                pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Enfermedad cerebrovascular. Elija alimentos y bebidas saludables. Elegir comidas y refrigerios saludables puede ayudar a prevenir el accidente cerebrovascular. ... Mantenga un peso saludable. ... Haga actividad física con regularidad. ... No fume. ... Limite la ingesta de alcohol. ... Controle su colesterol. ... Controle su presión arterial. ... Controle la diabetes.")
            if j == 10 and str(row[10]) == "Si":
                pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Diabetes. Bajar el exceso de peso. Bajar de peso reduce el riesgo de diabetes. ... Haz más actividad física. La actividad física regular tiene muchos beneficios. ... Consume alimentos vegetales saludables. ... Consume grasas saludables. ... Omite las dietas relámpago y toma decisiones más saludables.")
            if j == 11 and str(row[11]) == "Si":
                pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Dislipidemias. Se debe disminuir el consumo de grasa, especialmente la grasa saturada, evite el consumo de carnes con alto contenido de grasa, vísceras, piel, gordos, huesos para hacer caldos, manteca, mantequillas y salsas.")
            if j == 12 and str(row[12]) == "Si":
                pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Enfermedad renal. Coma comidas saludables y disminuya la sal y azúcar añadidos. Ingiera menos de 2300 miligramos de sodio diarios. Trate de que menos del 10 por ciento de sus calorías diarias provengan de azúcares añadidos. Escoja alimentos saludables para su cuerpo.")
            if (j>=13 and j<=19) and str(row[j]) == "Si":
                if b < 1:
                    pdf.ln(10)
                    pdf.set_font('Times','B',14.0) 
                    pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Diagnósticos Própios")
                    pdf.ln(10)
                b+=1
            pdf.set_font('Times','',10.0)
            if j == 13 and str(row[13]) == "Si":
                pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Hipertensión arterial. Reduce el exceso de peso y cuida la cintura. ... Haz ejercicio regularmente. ... Lleva una dieta saludable. ... Reduce la sal (sodio) en tu alimentación. ... Limita el consumo de alcohol. ... Dejar de fumar. ... Descansa bien durante la noche.")
            if j == 14 and str(row[14]) == "Si":
                pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Enfermedades Cardiovasculares. No fumes ni consumas tabaco. ... Muévete: intenta hacer al menos de 30 a 60 minutos de actividad al día. ... una dieta saludable para el corazón. ... mantener un peso saludable. ... Sueño de buena calidad. ... Controla el estrés. ... Preséntate a exámenes médicos regulares.")
            if j == 15 and str(row[15]) == "Si":
                pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Exposición a tóxicos. Retira todo lo que quede en la boca de la persona. Si sospechas que la sustancia tóxica es un producto de limpieza de uso doméstico u otra sustancia química, lee la etiqueta del recipiente y sigue las instrucciones para casos de intoxicación involuntaria.")
            if j == 16 and str(row[16]) == "Si":
                pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Enfermedad cerebrovascular. Elija alimentos y bebidas saludables. Elegir comidas y refrigerios saludables puede ayudar a prevenir el accidente cerebrovascular. ... Mantenga un peso saludable. ... Haga actividad física con regularidad. ... No fume. ... Limite la ingesta de alcohol. ... Controle su colesterol. ... Controle su presión arterial. ... Controle la diabetes.")
            if j == 17 and str(row[17]) == "Si":
                pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Diabetes. Bajar el exceso de peso. Bajar de peso reduce el riesgo de diabetes. ... Haz más actividad física. La actividad física regular tiene muchos beneficios. ... Consume alimentos vegetales saludables. ... Consume grasas saludables. ... Omite las dietas relámpago y toma decisiones más saludables.")
            if j == 18 and str(row[18]) == "Si":
                pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Dislipidemias. Se debe disminuir el consumo de grasa, especialmente la grasa saturada, evite el consumo de carnes con alto contenido de grasa, vísceras, piel, gordos, huesos para hacer caldos, manteca, mantequillas y salsas.")
            if j == 19 and str(row[19]) == "Si":
                pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Enfermedad renal. Coma comidas saludables y disminuya la sal y azúcar añadidos. Ingiera menos de 2300 miligramos de sodio diarios. Trate de que menos del 10 por ciento de sus calorías diarias provengan de azúcares añadidos. Escoja alimentos saludables para su cuerpo.")
            if (j >= 20 and j <= 27) and str(row[j]) == "Si":
                if c < 1:
                    pdf.ln(10)
                    pdf.set_font('Times','B',14.0) 
                    pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Uso de medicamentos y/o sustancias:")
                    pdf.ln(10)
                c+=1
            pdf.set_font('Times','',10.0)
            if j == 20 and str(row[20]) == "Si":
                pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Alcohol. Evite las personas o lugares que lo hagan beber cuando usted no desea hacerlo, o que lo tienten a beber más de lo que debería. Planee otras actividades que no impliquen beber para los días en que tenga ganas de tomar. Mantenga el alcohol fuera de su hogar. Elabore un plan para manejar sus ganas de beber.")
            if j == 21 and str(row[21]) == "Si":
                pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Cocaína. Piensa si verdaderamente quieres dejar la cocaína. Habla con tu pareja y familiares más allegados del problema. Pide ayuda profesional a médicos y psicólogos especialistas en adicciones.")
            if j == 22 and str(row[22]) == "Si":
                pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Anfetaminas. Consulta a un profesional de la salud. Establece metas alcanzables. Busca apoyo social. Evita situaciones de riesgo. Adopta un estilo de vida saludable. Busca ayuda profesional. Considera la desintoxicación supervisada. Establece nuevas rutinas. Aprende a manejar el estrés. Celebra tus logros.")
            if j == 23 and str(row[23]) == "Si":
                pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Cafeína. Consulta a un profesional de la salud. Establece metas alcanzables. Busca apoyo social. Evita situaciones de riesgo. Adopta un estilo de vida saludable. Busca ayuda profesional. Considera la desintoxicación supervisada. Establece nuevas rutinas. Aprende a manejar el estrés. Celebra tus logros.")
            if j == 24 and str(row[24]) == "Si":
                pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Antidepresivos. Habla y desahógate. No tomes decisiones precipitadas. Sé sincero. Piensa en positivo. No te encierres en ti mismo. Muévete. Come y duerme bien. Intenta evitar el estrés. No abuses del alcohol u otras drogas. Cumple el tratamiento médico.")
            if j == 25 and str(row[25]) == "Si":
                pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Descongestionantes. Esta es una oración de ejemplo que podría continuar en el próximo renglón si se desborda.")  
            if j == 26 and str(row[26]) == "Si":
                pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "AINES. Asegúrese de informar a los profesionales que le atiendan acerca de TODOS los medicamentos que esté tomando: medicamentos recetados, medicamentos de venta libre o medicinas a base de hierbas. Si tiene algún factor de riesgo, valorarán la necesidad de indicarle algún protector gástrico. Tome el medicamento preferentemente con el estómago lleno. No supere la dosis que le han pautado. Continúe el tratamiento solo durante el tiempo que sea necesario. Si le cambian el tipo de AINE, acuérdese de dejar de tomar el anterior. Asegúrese de que conoce si algún medicamento de uso habitual de los que guarda en casa es un AINE. Puede ser útil escribirlo en la caja.")
            if j == 27 and str(row[27]) == "Si":
                pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Anticonceptivos orales. Consulta a un profesional de la salud. Comprende los diferentes tipos. Toma la píldora a la misma hora todos los días. Entiende los posibles efectos secundarios. Combínalos con otros métodos. Mantén un suministro constante. Comprende la importancia de las interacciones medicamentosas. Realiza chequeos periódicos. No te saltes las dosis. Considera tu salud a largo plazo.")
            if (j == 28) and str(row[j]) == "Si":
                pdf.ln(10)
                pdf.set_font('Times','B',14.0) 
                pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Estilo de vida:")  
                pdf.ln(10)
            pdf.set_font('Times','',10.0)
            if j == 28 and str(row[28]) == "Si":
                pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Consumes comidas rápidas o alimentos procesados. Planificación de comidas. Educación nutricional. Incrementa la ingesta de frutas y verduras. Explora recetas saludables. Limita gradualmente la comida rápida. Establece horarios de comida regulares. Hidratación adecuada. Lleva tus propios snacks. Aprende a leer etiquetas nutricionales. Encuentra alternativas saludables.")
            if (j >= 29 and j <=37) and str(row[j]) == "Si":
                if d<1:
                    pdf.ln(10)
                    pdf.set_font('Times','B',14.0) 
                    pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Valoración cefalocaudal:")  
                    pdf.ln(10)
                d+=1
            pdf.set_font('Times','',10.0)
            if j == 29 and str(row[29]) == "Si":
                pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Dolor de cabeza. Hidratación. Descanso y sueño. Alivio del estrés. Evitar desencadenantes alimentarios. Postura adecuada. Descansos visuales. Analgésicos de venta libre. Compresas frías o calientes. Evitar o moderar la cafeína. Masajes. Aromaterapia. Consulta médica.")
            if j == 30 and str(row[30]) == "Si":
                pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Nerviosismo. Prácticas de relajación. Ejercicio regular. Establece rutinas. Descanso adecuado. Limita la cafeína y azúcares. Habla sobre tus preocupaciones. Establece metas alcanzables. Evita la procrastinación. Aprende a decir 'no'. Practica la gratitud. Tiempo para actividades recreativas. Consulta profesional.")
            if j == 31 and str(row[31]) == "Si":
                pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Sangrado por la nariz. Inclinación hacia adelante y cabeza levantada. Suénate la nariz suavemente. Presiona la nariz con pulgar e índice. Continúa presionando entre 10 y 15 minutos. Repite si el sangrado persiste después de 15 minutos. Evita introducir los dedos en la nariz o bajar la cabeza. Aplica gel salino, ungüento antibiótico o vaselina en la nariz. Evita bajar la cabeza por debajo del corazón o levantar objetos pesados. Usa vapor, humidificadores o compresa de hielo para prevenir otro sangrado. En caso de un nuevo sangrado, repite los pasos y aplica un atomizador nasal con oximetazolina. Busca ayuda médica si el sangrado persiste.")
            if j == 32 and str(row[32]) == "Si":
                pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Silbido o zumbido. Usa protección auditiva. Baja el volumen. Usa ruido blanco. Limita el consumo de alcohol, cafeína y nicotina.")
            if j == 33 and str(row[33]) == "Si":
                pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Mareo. Siéntate o acuéstate de inmediato cuando te sientas mareado. Mantente acostado sin moverte con los ojos cerrados en una habitación oscura si estás atravesando un episodio serio de vértigo.")
            if j == 34 and str(row[34]) == "Si":
                pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Visión borrosa. Usa gafas de sol con filtros seguros para minimizar el impacto de los rayos ultravioleta. Consume una dieta saludable y balanceada que le brinde a tu cuerpo los minerales y las vitaminas que requiere para el buen estado de la vista, como la vitamina A, vitamina C y vitamina E. Realiza actividad física con frecuencia.")
            if j == 35 and str(row[35]) == "Si":
                pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Palpitaciones. Practicar técnicas de relajación. Reducir o eliminar el consumo de estimulantes. Estimular el nervio vago. Mantener el equilibrio de los electrolitos. Mantenerse hidratado. Evitar el consumo excesivo de alcohol. Hacer ejercicio regularmente.")
            if str(row[36]) == "Si" and j == 36:
                pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Cansancio constante. Mantenga un diario de fatiga para identificar patrones diarios. Realice ejercicio regularmente, considerando actividades como tai chi o yoga. Evite siestas largas (más de 30 minutos) tarde en el día. Deje de fumar para mejorar la salud general y aumentar la energía. Pida ayuda si se siente abrumada para compartir tareas y reducir el estrés.")
            if str(row[j]) == "Si" and j >36:
                pdf.multi_cell(page_width - 2 * pdf.l_margin, 5, "Hinchazón. Consumir diariamente al menos 5 piezas de frutas y verduras, combinando cocinado y crudo. Reducir el consumo de proteína animal y aumentar la ingesta de proteína vegetal para incorporar fibra a la dieta. Optar por cereales integrales en lugar de refinados, combinados con legumbres para obtener proteína vegetal de calidad. Aumentar el consumo de pescado azul pequeño al menos 2 veces por semana para obtener omega-3. Utilizar aceite de oliva virgen extra tanto para cocinar como para aliños. Incorporar especias para dar sabor a las comidas y reducir el consumo de sal. Beber suficiente agua diariamente, adaptando la cantidad a las necesidades individuales. Realizar ejercicio moderado de forma regular para mantener un estilo de vida activo y saludable.")
            
    pdf.ln(10)
    return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf', headers={'Content-Disposition':'attachment;filename=INFORME.pdf'})

@app.route('/truncate_usuarios')
def truncate_usuarios():
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect('database/medic_app.db')
        cursor = conn.cursor()

        # Ejecutar el comando TRUNCATE
        cursor.execute('DELETE FROM usuarios;')

        # Confirmar los cambios
        conn.commit()

        # Cerrar la conexión
        conn.close()

        return "Tabla 'usuarios' truncada exitosamente."
    except Exception as e:
        return f"Error al truncar la tabla 'usuarios': {str(e)}"

@app.route('/error')
def error():
    return render_template('error.html')

if __name__ == '__main__':
    app.run(debug=True)