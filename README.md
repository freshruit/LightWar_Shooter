# LightWar Shooter

Вдохновившись играми `Serious Sam` и `DOOM`, мы решили написать свою игру с 3D-графикой.

**Наш выбор пал на игру от первого лица с ограниченным миром, где основной целью является уничтожение монстров(3D-шутер).**

## Информация

Проект представляет собой игру от первого лица с реализованными возможностями:

- передвигаться по игровому полю

- уничтожать монстров (счётчик оставшихся располагается в левом верхнем углу)

- просматривать местоположение персонажа и монстров относительно игрового поля (карта располагается в левом верхнем углу)

- отслеживать время прохождения карты для поддержания лидерской позиции (таймер располагается в левом верхнем углу)

- отслеживать скорость виртуализации, число кадров в секунду (FPS), для обзора производительности кода на разных ПК

- отслеживать здоровье персонажа, чтобы не проиграть

- просматривать таблицу лидеров (создана для мотивации играть)

## Игровое окно

В момент запуска приложения вас встречает окно с требованием ввести никнейм.

Используя клавиатуру, введите свой никнейм и нажмите клавишу `Enter`.

Впоследствии он будет отображаться в базе данных и таблице лидеров,
а так же вы сможете просматривать текущее положение по уровням в левом верхнем углу главного меню.


Далее вас встречают три кнопки интерфейса:

- `Играть` (отвечает за виртуализацию уровня на экране)

- `Лидеры` (отображает список игроков, прошедших 5-ый уровень, которые затратили на него меньше всего времени)

- `Выйти` (для завершения игрового процесса)

## Запуск

Для правильного запуска приложения вам потребуется язык программирования `Python 3.9.6`
(стабильная работа приложения гарантируется именно на этой версии).
Его вы сможете скачать по этой ссылке: [тык](https://www.python.org/downloads/release/python-396/)

Далее вам нужно установить внешние зависимости.
Для этого откройте папку с проектом `LightWar` и, зажав `Shift`, нажмите в пустой области правой кнопкой мыши и выберите
"Открыть окно `PowerShell` здесь"
вставьте команду `pip install -r requirements.txt` и нажмите `Enter`.

Далее вы можете пойти двумя путями:
1) прописать там же (в PowerShell) `python main.py`
2) запустить `LightWar.exe` в папке с проектом

## Игровой процесс

После нажатия кнопки `Играть` вы появляетесь в игровом мире, где ваша цель - уничтожить всех монстров за минимальное время.

При этом не забывайте, что монстры также наносят урон, поэтому не дайте им себя победить!

Для передвижения используются клавиши `W`, `A`, `S`, `D`.

Для смены угла обзора используется `мышь`.

**Монстры отображены на карте красным цветом, персонаж зелёным цветом.**

`Важно!` После прохождения очередного уровня, чтобы сохранить прогресс, вам нужно выйти в игровое меню.

По завершении `5 уровня` вы получите уведомление в главном меню, что `игра завершена`!