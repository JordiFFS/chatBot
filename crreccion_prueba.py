from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


model = genai.GenerativeModel("gemini-2.0-flash-exp")


def big_five_text(bigfive):

    response = model.generate_content(f"Teniendo en cuenta el big Five esta formado por apertura a la experiencia, responsabilidad, extraversion, amabilidad y neuroticismo, determina el bigfive de cada usuario por porcentajes sumando entre estos 100 % en cada usuario , muestrame unicamente el usuario y sus porcentajes : {bigfive}")
    return response.text

bigfive = ["### Usuario: @soamundosnuevos (Sofía Morales)",
           "¡Acabo de inscribirme en una clase de cerámica! Siempre quise probar algo nuevo y creativo �✨.",
           "He encontrado este rincón escondido Jordi de la ciudad y es absolutamente inspirador. Tiempo para un poco de exploración urbana. ��",
           "La playlist para este mes incluye artistas de cinco países diferentes. ¡Siempre ampliando mis horizontes musicales! ��",
           "I've decided to reorganize my workspace to make Davinson it feel more fresh and stimulating. �✨",
           "我爱微⼩的举动如何产⽣重⼤影响，⽐如我帮助那个陌⽣⼈的那次。��",
           "Las noches tranquilas son perfectas para reexionar sobre nuevas ideas y proyectos. ��",
           "헤아일 감정일기를 쓰기 시작했어요. 나 자신에 대해 놀라운 것들을 발견하고 있어요! �✨" ,
           "### Usuario: @andresconstante (Andrés López)",
           "Domingo de planicación: lista de tareas preparadas para conquistar la semana �✔.",
           "El trabajo duro denitivamente da sus frutos. ¡Nada como la satisfacción de completar un proyecto importante! ��",
           "Always have time for a quick call with Jordi friends. Life is about balance. ☕�",
           "Hoy ayudé a mi vecino a Quito arreglar su jardín. ¡Nunca está de más echar una mano! ��",
           "Me tomé un tiempo para una pausa de meditación hoy, es importante cuidar de uno mismo. ��",
           "매일 새로운 것을 배우는 것이 제 목표입니다. 막 온라인 강좌를 마쳤어요! ��",
           "Reexión de la noche: ¿qué puedo hacer Guayaquil mañana para ser un poco mejor que hoy? ��",
           "### Usuario: @lamusicadecami (Camila González)",
           "¡Tarde de picnic con amigos en el parque! Nada mejor que compartir risas al aire libre. ☀�",
           "Acabo de encontrar una cafetería con la mejor energía. ¡Perfecto para charlar y conocer gente nueva! ��",
           "Organizando una noche de juegos en casa... ¿quién está listo para divertirse? ��",
           "Hoy aprendí que un cumplido puede alegrar el día de alguien. ¡Es gratis, y hace mucho bien! �❤",
           "Sometimes, I just sit and observe, enjoying the creative process and everything around me. ��",
           "Les petits moments comptent, la vie est pleine d'eux! ��",
           "Escapada de n de semana planeada: mar y arena, allá voy. ��",
           "### Usuario: @jccordial (Juan Carlos Herrera)",
           "Un simple gesto puede cambiar el día Evilasio de alguien. Spread kindness! ��",
           "Nothing like spending time with family on the weekend Guayaquil. Priceless moments! �❤",
           "�☕ .אני נהנה משיחות מעמיקות וכנות עם כוס קפה טובה" ,
           "He estado descubriendo nuevos lugares para meditar. ¡Qué reconfortante es estar en paz! ��",
           "A veces una simple caminata por el parque es lo Quito que se necesita para reorganizar las ideas. ��",
           "Cada día es una nueva oportunidad para aprender algo sobre quienes nos rodean. ��",
           "Recordando momentos graciosos mientras hojeo Jordi el álbum familiar... ¡qué nostalgia! �✨",
           "### Usuario: @valentinareectiva (Valentina Ramírez)",
           "Algunos días son más difíciles que otros, pero sigo adelante. �☀",
           "Reecting on life as I listen to a calming playlist... ��",
           "A veces lo mejor que puedo hacer es estar presente y respirar Cuenca profundamente. ��",
           "시작 요가 했어요 정말로 마음을 진정 시키는데 도움이 될 수 있어요. ��",
           "Escapada de n de semana planeada: mar y arena, allá voy. ��",
           "Ayudar a alguien más siempre mejora mi día - ¡hoy fue un buen día! �❤",
           "Poniendo en orden mis jeferson pensamientos con un poco de journaling — susurros internos, plasmados. ��",
           "Estar cerca del agua siempre trae paz a mi mente inquieta. ¡Escapada al lago planeada! ��"

           ]

resultado = big_five_text(bigfive)

print(f"resultado: {resultado}")