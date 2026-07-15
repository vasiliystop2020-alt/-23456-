import streamlit as st
import random
import base64

# Настройка страницы
st.set_page_config(page_title="С Днем Рождения, Мама!", page_icon="🃏", layout="wide")

# Функция для конвертации аудио в формат, понятный браузеру
def get_audio_html(file_path, loop=False, autoplay=False, element_id=""):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            loop_attr = "loop" if loop else ""
            autoplay_attr = "autoplay" if autoplay else ""
            id_attr = f"id='{element_id}'" if element_id else ""
            return f"""<audio {id_attr} {autoplay_attr} {loop_attr} style="display:none;">
                        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                       </audio>"""
    except FileNotFoundError:
        return ""

# Загружаем фоновую музыку и звук клика
bg_music_html = get_audio_html("bg_music.mp3", loop=True, autoplay=True, element_id="bg-music")
click_sound_html = get_audio_html("click_sound.mp3", loop=False, autoplay=False, element_id="click-sound")

# Внедряем аудио на страницу
st.markdown(bg_music_html, unsafe_allow_html=True)
st.markdown(click_sound_html, unsafe_allow_html=True)

# Скрипт для воспроизведения звука клика при нажатии на ЛЮБУЮ кнопку Streamlit
st.markdown("""
    <script>
    const playClick = () => {
        const audio = window.parent.document.getElementById('click-sound');
        if (audio) {
            audio.currentTime = 0;
            audio.play().catch(e => console.log("Звук заблокирован браузером"));
        }
    };
    
    // Находим все кнопки на странице и добавляем им звук клика
    const updateButtons = () => {
        const buttons = window.parent.document.querySelectorAll('button');
        buttons.forEach(btn => {
            if (!btn.dataset.soundAdded) {
                btn.addEventListener('click', playClick);
                btn.dataset.soundAdded = "true";
            }
        });
    };

    // Следим за изменениями на странице, чтобы озвучивать новые появляющиеся кнопки
    const observer = new MutationObserver(updateButtons);
    observer.observe(window.parent.document.body, { childList: true, subtree: true });
    updateButtons();
    </script>
""", unsafe_allow_html=True)

# Заголовок пасьянса
st.markdown("<h1 style='text-align: center; color: #ff4b4b;'>🃏 Праздничный Пасьянс для Мамы! 🎉</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px;'>Любимая мамочка, разложи этот классический пасьянс, чтобы открыть праздничный сюрприз!</p>", unsafe_allow_html=True)

# Примечание для мамы о звуке (браузеры часто блокируют автозвук до первого клика)
st.caption("🎵 Если не слышно музыки, просто нажмите на любую кнопку на экране, чтобы включить звук!")

# Инициализация колоды и состояния игры
SUITS = ['♥️', '♦️', '♣️', '♠️']
VALUES = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

if 'deck' not in st.session_state:
    full_deck = [{'suit': s, 'value': v, 'color': 'red' if s in ['♥️', '♦️'] else 'black'} for s in SUITS for v in VALUES]
    random.shuffle(full_deck)
    
    st.session_state.tableaux = []
    cursor = 0
    for i in range(1, 8):
        pile = full_deck[cursor:cursor+i]
        cursor += i
        st.session_state.tableaux.append({
            'cards': pile,
            'visible_from': i - 1
        })
    
    st.session_state.stock = full_deck[cursor:]
    st.session_state.waste = []
    st.session_state.foundations = {s: [] for s in SUITS}
    st.session_state.game_won = False

# Функция для отображения карты
def render_card(card, hidden=False):
    if hidden:
        return "<div style='border: 2px solid #333; background-color: #ff4b4b; height: 100px; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;'>🎴</div>"
    color_style = "color: red;" if card['color'] == 'red' else "color: black;"
    return f"<div style='border: 2px solid #ccc; background-color: white; height: 100px; border-radius: 8px; display: flex; flex-direction: column; align-items: center; justify-content: center; {color_style} font-weight: bold; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);'><div style='font-size: 20px;'>{card['value']}</div><div>{card['suit']}</div></div>"

# Игровое поле: Верхняя панель (Колода, Сброс и Дома мастей)
col_stock, col_waste, col_empty, col_f1, col_f2, col_f3, col_f4 = st.columns([1.5, 1.5, 1, 1, 1, 1, 1])

with col_stock:
    st.write("Колода")
    if st.session_state.stock:
        if st.button("🔄 Взять карту", key="draw_btn"):
            st.session_state.waste.append(st.session_state.stock.pop(0))
            st.rerun()
    else:
        if st.session_state.waste:
            if st.button("Перевернуть сброс", key="reset_stock_btn"):
                st.session_state.stock = st.session_state.waste[::-1]
                st.session_state.waste = []
                st.rerun()
        st.caption("Пусто")

with col_waste:
    st.write("Сброс")
    if st.session_state.waste:
        st.markdown(render_card(st.session_state.waste[-1]), unsafe_allow_html=True)
    else:
        st.caption("Пусто")

# Отображение домов
foundation_cols = [col_f1, col_f2, col_f3, col_f4]
for idx, suit in enumerate(SUITS):
    with foundation_cols[idx]:
        st.write(f"Дом {suit}")
        cards_in_f = st.session_state.foundations[suit]
        if cards_in_f:
            st.markdown(render_card(cards_in_f[-1]), unsafe_allow_html=True)
        else:
            st.markdown("<div style='border: 2px dashed #ccc; height: 100px; border-radius: 8px;'></div>", unsafe_allow_html=True)

st.divider()

# Игровое поле: Нижняя панель
st.write("### Игровое поле")
tableaux_cols = st.columns(7)

for idx in range(7):
    with tableaux_cols[idx]:
        st.write(f"Стопка {idx+1}")
        pile_data = st.session_state.tableaux[idx]
        cards = pile_data['cards']
        visible_idx = pile_data['visible_from']
        
        if not cards:
            st.markdown("<div style='border: 2px dashed #eee; height: 100px; border-radius: 8px; text-align: center; line-height: 100px; color: #ccc;'>Пусто</div>", unsafe_allow_html=True)
        else:
            for c_idx, card in enumerate(cards):
                is_hidden = c_idx < visible_idx
                if c_idx >= len(cards) - 1:
                    st.markdown(render_card(card, hidden=is_hidden), unsafe_allow_html=True)
            
            if visible_idx < len(cards) and st.button("В дом", key=f"move_{idx}"):
                top_card = cards[-1]
                f_pile = st.session_state.foundations[top_card['suit']]
                
                is_valid = False
                if not f_pile and top_card['value'] == 'A':
                    is_valid = True
                elif f_pile:
                    current_top_val = f_pile[-1]['value']
                    if VALUES.index(top_card['value']) == VALUES.index(current_top_val) + 1:
                        is_valid = True
                
                if is_valid:
                    f_pile.append(cards.pop())
                    if len(cards) == visible_idx and visible_idx > 0:
                        st.session_state.tableaux[idx]['visible_from'] -= 1
                    st.rerun()
                else:
                    st.toast("Эту карту пока нельзя положить в дом!", icon="⚠️")

# Проверка победы
total_founded = sum(len(st.session_state.foundations[s]) for s in SUITS)
if total_founded == 52:
    st.session_state.game_won = True

st.divider()

# Праздничное поздравление
show_congrats = st.session_state.game_won or st.checkbox("Мама, нажми сюда, чтобы открыть открытку сразу! 🎁")

if show_congrats:
    st.balloons()
    st.markdown("""
        <div style='background-color: #ffe6e6; padding: 30px; border-radius: 20px; text-align: center; border: 3px dashed #ff4b4b; margin-top: 20px;'>
            <h2 style='color: #d93838; margin-bottom: 15px;'>🎁 Любимая мамочка, с днем рождения! 🎁</h2>
            <p style='font-size: 20px; color: #333; line-height: 1.6; font-weight: bold;'>
                Пусть каждый твой день будет наполнен радостью, улыбками и теплом! <br>
                Желаю тебе самого крепкого здоровья, отличного настроения и исполнения всех желаний. <br>
                Спасибо за твою доброту и бесконечную заботу. Я тебя очень сильно люблю! ❤️
            </p>
        </div>
    """, unsafe_allow_html=True)

# Кнопка перезапуска
if st.button("Начать пасьянс заново 🔄"):
    del st.session_state['deck']
    st.rerun()
