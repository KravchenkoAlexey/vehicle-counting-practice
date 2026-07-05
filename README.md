# Vehicle Counting — практика (вариант 11)

Подсчёт транспорта на дорожном видео: обучение и сравнение моделей детекции (раздел 2) и веб-приложение на Django (раздел 3).

**Автор:** [KravchenkoAlexey](https://github.com/KravchenkoAlexey)

## Содержание репозитория

| Папка | Описание |
|-------|----------|
| `vehicle-counting/` | Jupyter-ноутбуки, метрики, графики, веса лучшей модели YOLOv8s |
| `kod/` | Django-сайт: загрузка видео, детекция, трекинг, подсчёт, отчёты |

**Не включено в репозиторий** (скачивается или хранится локально):

- датасет (см. ссылку ниже);
- веса остальных моделей (SSD300, Faster R-CNN, RetinaNet, RT-DETR-l);
- текстовый отчёт по практике.

## Датасет

**AI Traffic System** (Roboflow Universe), 7 классов: bicycle, bus, car, motorbike, rickshaw, truck, van.

- Ссылка: https://universe.roboflow.com/object-detection-sn8ac/ai-traffic-system/dataset/1  
- После скачивания распакуйте датасет и укажите путь в `vehicle-counting/data.yaml` (поле `path`).

## Результаты обучения (тестовая выборка)

| Модель | mAP@0.5 | FPS |
|--------|---------|-----|
| **YOLOv8s** | **0.586** | **86** |
| RT-DETR-l | 0.563 | 34 |
| Faster R-CNN | 0.536 | 17 |
| RetinaNet | 0.458 | 19 |
| SSD300 | 0.303 | 59 |

Подробные метрики: `vehicle-counting/results/all_metrics.json`, `comparison.xlsx`.

В веб-приложении используется **YOLOv8s** (`vehicle-counting/runs/detect/yolov8s/weights/best.pt`).

## Требования

- Python 3.10+
- NVIDIA GPU с CUDA (рекомендуется; на CPU работает медленнее)
- ~4 ГБ свободного места (веса + зависимости)

## Установка и запуск сайта

Репозиторий должен быть клонирован целиком — папки `kod/` и `vehicle-counting/` лежат **рядом** в корне.

```bash
git clone https://github.com/KravchenkoAlexey/vehicle-counting-practice.git
cd vehicle-counting-practice/kod
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Откройте в браузере: http://127.0.0.1:8000/

### Возможности сайта

- загрузка видео **MP4 / AVI**;
- детекция YOLOv8s + трекинг ByteTrack;
- подсчёт bus, car, truck, van при пересечении линии;
- история сессий, снимки кадров, выгрузка Excel-отчёта.

Загруженные видео сохраняются локально в `kod/data/uploads/` (в git не попадают).

## Обучение моделей (ноутбуки)

```bash
cd vehicle-counting
pip install ultralytics torch torchvision opencv-python pandas openpyxl torchmetrics jupyter
jupyter notebook
```

| Ноутбук | Назначение |
|---------|------------|
| `dataset_check.ipynb` | проверка датасета по 8 критериям |
| `train_eval.ipynb` | обучение 5 моделей, метрики, примеры детекций |

Перед запуском обновите путь к датасету в `data.yaml`. В ноутбуке `train_eval.ipynb` установлен `SKIP_TRAIN = True` — повторное обучение не запускается, используются сохранённые результаты.

## Структура проекта

```
vehicle-counting-practice/
├── README.md
├── vehicle-counting/
│   ├── data.yaml
│   ├── dataset_check.ipynb
│   ├── train_eval.ipynb
│   ├── results/              # метрики, графики, примеры
│   └── runs/detect/yolov8s/weights/best.pt
└── kod/
    ├── manage.py
    ├── config.py
    ├── video_counter.py
    ├── requirements.txt
    └── counting/             # Django-приложение
```

## Видео и GitHub

**В репозиторий видео класть не нужно.**

| Способ | Ограничения |
|--------|-------------|
| Обычный файл в git | до **100 МБ** на файл; репозиторий быстро раздувается |
| Git LFS | для крупных файлов, но есть лимиты трафика и хранилища |
| Сайт (локально) | видео загружаются через форму на http://127.0.0.1:8000/ — так и задумано |

Для демонстрации преподавателю достаточно запустить сайт у себя и обработать видео на компьютере. Тестовые ролики храните локально или в облаке (Google Drive, Яндекс.Диск), а в отчёт можно вставить скриншоты из `results/` или снимки со страницы результата.

## Лицензия

Учебный проект. Датасет — условия Roboflow Universe; код моделей — Ultralytics / PyTorch (см. лицензии библиотек).
