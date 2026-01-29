
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from typing import Dict, List, Tuple, Any
import json
import warnings
warnings.filterwarnings('ignore')


class AnalizadorInteligente:
    """Analiza datos de Excel y genera insights automáticamente"""
    
    def _init_(self, archivo_excel: str):
        """
        Args:
            archivo_excel: Ruta del archivo Excel a analizar
        """
        self.archivo = archivo_excel
        self.hojas_data = {}
        self.analisis = {
            'hojas': {},
            'relaciones': [],
            'graficos_recomendados': [],
            'insights': []
        }
        
    def cargar_datos(self):
        """Carga todas las hojas del Excel"""
        try:
            excel_file = pd.ExcelFile(self.archivo)
            for hoja in excel_file.sheet_names:
                self.hojas_data[hoja] = pd.read_excel(self.archivo, sheet_name=hoja)
            return True
        except Exception as e:
            raise Exception(f"Error al cargar Excel: {str(e)}")
    
    def detectar_tipo_columna(self, serie: pd.Series) -> str:
        """
        Detecta el tipo semántico de una columna
        
        Returns:
            'fecha', 'numerico', 'categorico', 'texto', 'booleano', 'id'
        """
        # Verificar valores nulos
        if serie.isna().all():
            return 'vacio'
        
        # Booleano
        if serie.dtype == bool or set(serie.dropna().unique()) <= {0, 1, True, False}:
            return 'booleano'
        
        # Fecha
        if pd.api.types.is_datetime64_any_dtype(serie):
            return 'fecha'
        try:
            pd.to_datetime(serie.dropna())
            return 'fecha'
        except:
            pass
        
        # Numérico
        if pd.api.types.is_numeric_dtype(serie):
            # Verificar si podría ser un ID
            if serie.is_unique and serie.min() > 0:
                return 'id'
            return 'numerico'
        
        # Categórico vs Texto
        valores_unicos = serie.nunique()
        total_valores = len(serie.dropna())
        
        if valores_unicos / total_valores < 0.5:  # Menos del 50% son únicos
            return 'categorico'
        
        return 'texto'
    
    def analizar_hoja(self, nombre_hoja: str, df: pd.DataFrame) -> Dict:
        """Analiza una hoja individual"""
        analisis_hoja = {
            'nombre': nombre_hoja,
            'dimensiones': {
                'filas': len(df),
                'columnas': len(df.columns)
            },
            'columnas': {},
            'estadisticas': {},
            'claves_potenciales': []
        }
        
        # Analizar cada columna
        for col in df.columns:
            tipo = self.detectar_tipo_columna(df[col])
            
            col_info = {
                'tipo': tipo,
                'valores_nulos': int(df[col].isna().sum()),
                'valores_unicos': int(df[col].nunique())
            }
            
            # Estadísticas específicas por tipo
            if tipo == 'numerico':
                col_info['estadisticas'] = {
                    'media': float(df[col].mean()),
                    'mediana': float(df[col].median()),
                    'std': float(df[col].std()),
                    'min': float(df[col].min()),
                    'max': float(df[col].max())
                }
            elif tipo == 'categorico':
                col_info['categorias'] = df[col].value_counts().head(10).to_dict()
            elif tipo == 'id':
                analisis_hoja['claves_potenciales'].append(col)
            
            analisis_hoja['columnas'][col] = col_info
        
        return analisis_hoja
    
    def detectar_relaciones(self) -> List[Dict]:
        """
        Detecta relaciones entre hojas basándose en:
        - Columnas con nombres similares
        - Columnas con valores coincidentes
        - Claves foráneas potenciales
        """
        relaciones = []
        hojas = list(self.hojas_data.keys())
        
        for i, hoja1 in enumerate(hojas):
            for hoja2 in hojas[i+1:]:
                df1 = self.hojas_data[hoja1]
                df2 = self.hojas_data[hoja2]
                
                # Buscar columnas con nombres similares o iguales
                for col1 in df1.columns:
                    for col2 in df2.columns:
                        # Columnas con el mismo nombre
                        if col1.lower() == col2.lower():
                            # Verificar si hay valores en común
                            valores_comunes = set(df1[col1].dropna()) & set(df2[col2].dropna())
                            
                            if len(valores_comunes) > 0:
                                porcentaje_coincidencia = (
                                    len(valores_comunes) / 
                                    max(df1[col1].nunique(), df2[col2].nunique()) * 100
                                )
                                
                                relacion = {
                                    'hoja1': hoja1,
                                    'columna1': col1,
                                    'hoja2': hoja2,
                                    'columna2': col2,
                                    'tipo': 'llave_directa',
                                    'valores_comunes': len(valores_comunes),
                                    'confianza': round(porcentaje_coincidencia, 2)
                                }
                                relaciones.append(relacion)
        
        return relaciones
    
    def calcular_correlaciones(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula correlaciones entre columnas numéricas"""
        columnas_numericas = df.select_dtypes(include=[np.number]).columns
        if len(columnas_numericas) < 2:
            return None
        
        return df[columnas_numericas].corr()
    
    def recomendar_graficos(self) -> List[Dict]:
        """
        Recomienda gráficos basándose en los tipos de datos
        """
        recomendaciones = []
        
        for nombre_hoja, df in self.hojas_data.items():
            analisis_hoja = self.analisis['hojas'][nombre_hoja]
            
            # Identificar tipos de columnas
            columnas_numericas = [col for col, info in analisis_hoja['columnas'].items() 
                                 if info['tipo'] == 'numerico']
            columnas_categoricas = [col for col, info in analisis_hoja['columnas'].items() 
                                   if info['tipo'] == 'categorico']
            columnas_fechas = [col for col, info in analisis_hoja['columnas'].items() 
                              if info['tipo'] == 'fecha']
            
            # Gráfico de líneas (para series temporales)
            if columnas_fechas and columnas_numericas:
                for fecha in columnas_fechas:
                    for num in columnas_numericas:
                        recomendaciones.append({
                            'tipo': 'linea',
                            'hoja': nombre_hoja,
                            'x': fecha,
                            'y': num,
                            'titulo': f'{num} a lo largo del tiempo',
                            'prioridad': 'alta'
                        })
            
            # Gráfico de barras (categórico vs numérico)
            if columnas_categoricas and columnas_numericas:
                for cat in columnas_categoricas[:2]:  # Limitar a 2 categóricas
                    for num in columnas_numericas[:2]:  # Limitar a 2 numéricas
                        # Solo si la categórica tiene pocas categorías
                        if analisis_hoja['columnas'][cat]['valores_unicos'] <= 15:
                            recomendaciones.append({
                                'tipo': 'barras',
                                'hoja': nombre_hoja,
                                'x': cat,
                                'y': num,
                                'titulo': f'{num} por {cat}',
                                'prioridad': 'media'
                            })
            
            # Histogramas (distribuciones numéricas)
            for num in columnas_numericas:
                recomendaciones.append({
                    'tipo': 'histograma',
                    'hoja': nombre_hoja,
                    'columna': num,
                    'titulo': f'Distribución de {num}',
                    'prioridad': 'baja'
                })
            
            # Gráfico de correlación (si hay múltiples numéricas)
            if len(columnas_numericas) >= 2:
                recomendaciones.append({
                    'tipo': 'correlacion',
                    'hoja': nombre_hoja,
                    'columnas': columnas_numericas,
                    'titulo': f'Correlaciones en {nombre_hoja}',
                    'prioridad': 'alta'
                })
            
            # Gráfico de pastel (para categóricas con pocas categorías)
            for cat in columnas_categoricas:
                if 2 <= analisis_hoja['columnas'][cat]['valores_unicos'] <= 8:
                    recomendaciones.append({
                        'tipo': 'pastel',
                        'hoja': nombre_hoja,
                        'columna': cat,
                        'titulo': f'Distribución de {cat}',
                        'prioridad': 'baja'
                    })
        
        # Ordenar por prioridad
        prioridad_orden = {'alta': 0, 'media': 1, 'baja': 2}
        recomendaciones.sort(key=lambda x: prioridad_orden[x['prioridad']])
        
        return recomendaciones
    
    def generar_grafico(self, recomendacion: Dict, output_path: str):
        """Genera un gráfico basado en la recomendación"""
        plt.figure(figsize=(12, 6))
        
        hoja = recomendacion['hoja']
        df = self.hojas_data[hoja]
        tipo = recomendacion['tipo']
        
        try:
            if tipo == 'linea':
                df_sorted = df.sort_values(recomendacion['x'])
                plt.plot(df_sorted[recomendacion['x']], 
                        df_sorted[recomendacion['y']], 
                        marker='o')
                plt.xlabel(recomendacion['x'])
                plt.ylabel(recomendacion['y'])
                plt.xticks(rotation=45)
                
            elif tipo == 'barras':
                agrupado = df.groupby(recomendacion['x'])[recomendacion['y']].mean()
                agrupado.plot(kind='bar')
                plt.xlabel(recomendacion['x'])
                plt.ylabel(f'Promedio de {recomendacion["y"]}')
                plt.xticks(rotation=45)
                
            elif tipo == 'histograma':
                plt.hist(df[recomendacion['columna']].dropna(), bins=30, edgecolor='black')
                plt.xlabel(recomendacion['columna'])
                plt.ylabel('Frecuencia')
                
            elif tipo == 'correlacion':
                corr = self.calcular_correlaciones(df)
                if corr is not None:
                    sns.heatmap(corr, annot=True, cmap='coolwarm', center=0,
                              square=True, linewidths=1, cbar_kws={"shrink": 0.8})
                    
            elif tipo == 'pastel':
                conteo = df[recomendacion['columna']].value_counts()
                plt.pie(conteo.values, labels=conteo.index, autopct='%1.1f%%')
            
            plt.title(recomendacion['titulo'])
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
            
        except Exception as e:
            plt.close()
            raise Exception(f"Error al generar gráfico: {str(e)}")
    
    def analizar_completo(self) -> Dict:
        """Ejecuta el análisis completo del archivo"""
        # Cargar datos
        self.cargar_datos()
        
        # Analizar cada hoja
        for nombre_hoja, df in self.hojas_data.items():
            self.analisis['hojas'][nombre_hoja] = self.analizar_hoja(nombre_hoja, df)
        
        # Detectar relaciones
        self.analisis['relaciones'] = self.detectar_relaciones()
        
        # Recomendar gráficos
        self.analisis['graficos_recomendados'] = self.recomendar_graficos()
        
        # Generar insights
        self.analisis['insights'] = self.generar_insights()
        
        return self.analisis
    
    def generar_insights(self) -> List[str]:
        """Genera insights textuales del análisis"""
        insights = []
        
        # Total de hojas y registros
        total_filas = sum(info['dimensiones']['filas'] 
                         for info in self.analisis['hojas'].values())
        insights.append(f"El archivo contiene {len(self.hojas_data)} hoja(s) "
                       f"con un total de {total_filas} registros")
        
        # Relaciones detectadas
        if self.analisis['relaciones']:
            insights.append(f"Se detectaron {len(self.analisis['relaciones'])} "
                          f"relación(es) entre las hojas")
            for rel in self.analisis['relaciones']:
                insights.append(
                    f"  • {rel['hoja1']}.{rel['columna1']} ↔ "
                    f"{rel['hoja2']}.{rel['columna2']} "
                    f"({rel['confianza']}% de coincidencia)"
                )
        
        # Columnas con valores nulos significativos
        for hoja, info in self.analisis['hojas'].items():
            for col, col_info in info['columnas'].items():
                porcentaje_nulos = (col_info['valores_nulos'] / 
                                   info['dimensiones']['filas'] * 100)
                if porcentaje_nulos > 20:
                    insights.append(
                        f"⚠ {hoja}.{col} tiene {porcentaje_nulos:.1f}% de valores nulos"
                    )
        
        return insights


def exportar_para_powerbi(analisis: Dict, output_json: str):
    """
    Exporta el análisis en formato JSON compatible con Power BI
    """
    # Preparar estructura para Power BI
    powerbi_data = {
        'metadata': {
            'hojas': []
        },
        'relaciones': [],
        'medidas_sugeridas': []
    }
    
    # Metadatos de hojas
    for nombre_hoja, info in analisis['hojas'].items():
        hoja_meta = {
            'nombre': nombre_hoja,
            'columnas': []
        }
        
        for col, col_info in info['columnas'].items():
            hoja_meta['columnas'].append({
                'nombre': col,
                'tipo': col_info['tipo'],
                'tipo_powerbi': mapear_tipo_powerbi(col_info['tipo'])
            })
        
        powerbi_data['metadata']['hojas'].append(hoja_meta)
    
    # Relaciones
    for rel in analisis['relaciones']:
        powerbi_data['relaciones'].append({
            'desde': {
                'tabla': rel['hoja1'],
                'columna': rel['columna1']
            },
            'hacia': {
                'tabla': rel['hoja2'],
                'columna': rel['columna2']
            },
            'cardinalidad': 'muchos_a_uno',
            'direccion_filtro': 'ambos'
        })
    
    # Medidas sugeridas
    for nombre_hoja, info in analisis['hojas'].items():
        for col, col_info in info['columnas'].items():
            if col_info['tipo'] == 'numerico':
                powerbi_data['medidas_sugeridas'].extend([
                    {
                        'nombre': f'Suma de {col}',
                        'expresion': f'SUM({nombre_hoja}[{col}])',
                        'formato': 'numero'
                    },
                    {
                        'nombre': f'Promedio de {col}',
                        'expresion': f'AVERAGE({nombre_hoja}[{col}])',
                        'formato': 'numero'
                    }
                ])
    
    # Guardar JSON
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(powerbi_data, f, ensure_ascii=False, indent=2)
    
    return output_json


def mapear_tipo_powerbi(tipo_python: str) -> str:
    """Mapea tipos de Python a tipos de Power BI"""
    mapeo = {
        'numerico': 'Int64',
        'texto': 'Text',
        'categorico': 'Text',
        'fecha': 'DateTime',
        'booleano': 'Boolean',
        'id': 'Int64'
    }
    return mapeo.get(tipo_python, 'Text')


# Ejemplo de uso
if _name_ == "_main_":
    analizador = AnalizadorInteligente("datos.xlsx")
    resultado = analizador.analizar_completo()
    
    print("=== ANÁLISIS COMPLETADO ===")
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    
    # Generar primer gráfico recomendado
    if resultado['graficos_recomendados']:
        primer_grafico = resultado['graficos_recomendados'][0]
        analizador.generar_grafico(primer_grafico, "grafico_1.png")
        print(f"\nGráfico generado: grafico_1.png")
    
    # Exportar para Power BI
    exportar_para_powerbi(resultado, "powerbi_metadata.json")
    print("Metadata para Power BI exportada: powerbi_metadata.json")
    
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import traceback
import json
from datetime import datetime
import zipfile

# Importar analizador inteligente
from analizador_inteligente import (
    AnalizadorInteligente,
    exportar_para_powerbi
)

app = Flask(_name_)
CORS(app)

# Configuración
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
GRAFICOS_FOLDER = 'graficos'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'docx', 'pdf'}

for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, GRAFICOS_FOLDER]:
    os.makedirs(folder, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['GRAFICOS_FOLDER'] = GRAFICOS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max


def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint para verificar que el servidor está funcionando"""
    return jsonify({
        'status': 'ok',
        'message': 'API funcionando correctamente',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/analyze', methods=['POST'])
def analyze_excel():
    """
    Analiza un archivo Excel completo
    Retorna: análisis completo con relaciones, tipos de datos, y recomendaciones
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No se envió ningún archivo'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'Archivo sin nombre'}), 400
        
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            return jsonify({'error': 'Solo se permiten archivos Excel'}), 400
        
        # Guardar archivo temporalmente
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)
        
        # Analizar archivo
        analizador = AnalizadorInteligente(input_path)
        resultado = analizador.analizar_completo()
        
        # Guardar análisis
        analisis_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        analisis_filename = f"analisis_{analisis_id}.json"
        analisis_path = os.path.join(app.config['OUTPUT_FOLDER'], analisis_filename)
        
        with open(analisis_path, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        
        # Generar metadata para Power BI
        powerbi_filename = f"powerbi_metadata_{analisis_id}.json"
        powerbi_path = os.path.join(app.config['OUTPUT_FOLDER'], powerbi_filename)
        exportar_para_powerbi(resultado, powerbi_path)
        
        # Limpiar archivo de entrada
        os.remove(input_path)
        
        return jsonify({
            'success': True,
            'analisis_id': analisis_id,
            'analisis': resultado,
            'archivos_generados': {
                'analisis_completo': analisis_filename,
                'powerbi_metadata': powerbi_filename
            }
        })
        
    except Exception as e:
        error_msg = traceback.format_exc()
        print(error_msg)
        return jsonify({
            'error': 'Error en el análisis',
            'details': str(e)
        }), 500


@app.route('/api/generate-charts', methods=['POST'])
def generate_charts():
    """
    Genera gráficos automáticamente basándose en el análisis
    Acepta: archivo Excel y opciones de gráficos
    Retorna: ZIP con todos los gráficos generados
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No se envió ningún archivo'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'Archivo sin nombre'}), 400
        
        # Opciones
        max_graficos = int(request.form.get('maxGraficos', 10))
        solo_prioridad_alta = request.form.get('soloPrioridadAlta', 'false').lower() == 'true'
        
        # Guardar archivo
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)
        
        # Analizar y generar gráficos
        analizador = AnalizadorInteligente(input_path)
        analizador.analizar_completo()
        
        recomendaciones = analizador.analisis['graficos_recomendados']
        
        # Filtrar si solo se quieren de prioridad alta
        if solo_prioridad_alta:
            recomendaciones = [r for r in recomendaciones if r['prioridad'] == 'alta']
        
        # Limitar número de gráficos
        recomendaciones = recomendaciones[:max_graficos]
        
        # Generar gráficos
        graficos_generados = []
        graficos_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for idx, rec in enumerate(recomendaciones, 1):
            grafico_filename = f"grafico_{graficos_id}_{idx}.png"
            grafico_path = os.path.join(app.config['GRAFICOS_FOLDER'], grafico_filename)
            
            try:
                analizador.generar_grafico(rec, grafico_path)
                graficos_generados.append({
                    'filename': grafico_filename,
                    'titulo': rec['titulo'],
                    'tipo': rec['tipo'],
                    'hoja': rec['hoja']
                })
            except Exception as e:
                print(f"Error generando gráfico {idx}: {e}")
        
        # Crear ZIP con todos los gráficos
        zip_filename = f"graficos_{graficos_id}.zip"
        zip_path = os.path.join(app.config['OUTPUT_FOLDER'], zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for grafico in graficos_generados:
                grafico_path = os.path.join(app.config['GRAFICOS_FOLDER'], grafico['filename'])
                zipf.write(grafico_path, grafico['filename'])
        
        # Limpiar
        os.remove(input_path)
        
        return send_file(
            zip_path,
            as_attachment=True,
            download_name=zip_filename,
            mimetype='application/zip'
        )
        
    except Exception as e:
        error_msg = traceback.format_exc()
        print(error_msg)
        return jsonify({
            'error': 'Error generando gráficos',
            'details': str(e)
        }), 500


@app.route('/api/analyze-and-visualize', methods=['POST'])
def analyze_and_visualize():
    """
    Endpoint TODO-EN-UNO
    Analiza el Excel, genera gráficos, y crea metadata para Power BI
    Retorna: JSON con análisis y URLs de archivos generados
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No se envió ningún archivo'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'Archivo sin nombre'}), 400
        
        # Guardar archivo
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)
        
        # ID único para esta sesión
        session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # PASO 1: Análisis completo
        analizador = AnalizadorInteligente(input_path)
        analisis = analizador.analizar_completo()
        
        # PASO 2: Guardar análisis
        analisis_filename = f"analisis_{session_id}.json"
        analisis_path = os.path.join(app.config['OUTPUT_FOLDER'], analisis_filename)
        
        with open(analisis_path, 'w', encoding='utf-8') as f:
            json.dump(analisis, f, ensure_ascii=False, indent=2)
        
        # PASO 3: Generar metadata para Power BI
        powerbi_filename = f"powerbi_{session_id}.json"
        powerbi_path = os.path.join(app.config['OUTPUT_FOLDER'], powerbi_filename)
        exportar_para_powerbi(analisis, powerbi_path)
        
        # PASO 4: Generar gráficos (solo prioridad alta/media, máximo 8)
        graficos_generados = []
        recomendaciones_filtradas = [
            r for r in analisis['graficos_recomendados']
            if r['prioridad'] in ['alta', 'media']
        ][:8]
        
        for idx, rec in enumerate(recomendaciones_filtradas, 1):
            grafico_filename = f"chart_{session_id}_{idx}.png"
            grafico_path = os.path.join(app.config['GRAFICOS_FOLDER'], grafico_filename)
            
            try:
                analizador.generar_grafico(rec, grafico_path)
                graficos_generados.append({
                    'id': idx,
                    'filename': grafico_filename,
                    'url': f'/api/graficos/{grafico_filename}',
                    'titulo': rec['titulo'],
                    'tipo': rec['tipo'],
                    'hoja': rec['hoja'],
                    'prioridad': rec['prioridad']
                })
            except Exception as e:
                print(f"Error generando gráfico {idx}: {e}")
        
        # Limpiar archivo de entrada
        os.remove(input_path)
        
        # Respuesta completa
        return jsonify({
            'success': True,
            'session_id': session_id,
            'resumen': {
                'total_hojas': len(analisis['hojas']),
                'total_relaciones': len(analisis['relaciones']),
                'total_graficos': len(graficos_generados)
            },
            'analisis': {
                'hojas': analisis['hojas'],
                'relaciones': analisis['relaciones'],
                'insights': analisis['insights']
            },
            'graficos': graficos_generados,
            'archivos_descargables': {
                'analisis_completo': {
                    'filename': analisis_filename,
                    'url': f'/api/descargar/{analisis_filename}'
                },
                'powerbi_metadata': {
                    'filename': powerbi_filename,
                    'url': f'/api/descargar/{powerbi_filename}'
                }
            }
        })
        
    except Exception as e:
        error_msg = traceback.format_exc()
        print(error_msg)
        return jsonify({
            'error': 'Error en el análisis completo',
            'details': str(e)
        }), 500


@app.route('/api/graficos/<filename>', methods=['GET'])
def serve_grafico(filename):
    """Sirve un gráfico generado"""
    try:
        return send_from_directory(app.config['GRAFICOS_FOLDER'], filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@app.route('/api/descargar/<filename>', methods=['GET'])
def descargar_archivo(filename):
    """Descarga archivos JSON generados"""
    try:
        return send_from_directory(
            app.config['OUTPUT_FOLDER'],
            filename,
            as_attachment=True
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@app.route('/api/powerbi-template', methods=['POST'])
def generar_template_powerbi():
    """
    Genera un script de Power Query (M) para importar datos
    con las relaciones ya configuradas
    """
    try:
        data = request.get_json()
        analisis = data.get('analisis')
        
        if not analisis:
            return jsonify({'error': 'No se proporcionó análisis'}), 400
        
        # Generar script M de Power Query
        script_m = generar_script_power_query(analisis)
        
        session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        script_filename = f"powerbi_script_{session_id}.m"
        script_path = os.path.join(app.config['OUTPUT_FOLDER'], script_filename)
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_m)
        
        return send_file(
            script_path,
            as_attachment=True,
            download_name=script_filename
        )
        
    except Exception as e:
        return jsonify({
            'error': 'Error generando template',
            'details': str(e)
        }), 500


def generar_script_power_query(analisis: dict) -> str:
    """Genera un script de Power Query (M) con las relaciones"""
    script = """// Script generado automáticamente para Power BI
// Importa las relaciones detectadas automáticamente

let
    // Cargar archivo Excel
    Source = Excel.Workbook(File.Contents("RUTA_AL_ARCHIVO.xlsx"), null, true),
    
"""
    
    # Agregar cada hoja
    for idx, (nombre_hoja, info) in enumerate(analisis['hojas'].items(), 1):
        script += f"""    // Hoja: {nombre_hoja}
    Sheet{idx} = Source{{[Item="{nombre_hoja}",Kind="Sheet"]}}[Data],
    Promoted{idx} = Table.PromoteHeaders(Sheet{idx}, [PromoteAllScalars=true]),
    
"""
    
    script += """    // Definir tipos de datos
"""
    
    # Agregar salida
    script += """in
    Promoted1
"""
    
    return script


if _name_ == '_main_':
    print("=" * 60)
    print("🚀 API de Análisis Inteligente de Datos")
    print("=" * 60)
    print("\nEndpoints disponibles:")
    print("  POST /api/analyze - Analizar archivo Excel")
    print("  POST /api/generate-charts - Generar gráficos")
    print("  POST /api/analyze-and-visualize - TODO EN UNO ⭐")
    print("  GET  /api/graficos/<file> - Obtener gráfico")
    print("  GET  /api/descargar/<file> - Descargar JSON")
    print("\nServidor iniciado en: http://localhost:5000")
    print("=" * 60)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )