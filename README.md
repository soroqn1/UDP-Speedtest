# Simple UDP Speedtest

Цей Python скрипт є простим інструментом для тестування пропускної здатності та надійності UDP з'єднання між двома точками. Він працює у двох режимах: сервер (приймач) та клієнт (відправник).

## Особливості

* **UDP-з'єднання:** Використовує протокол UDP для передачі даних.
* **Режим Сервера:** Приймає UDP-пакети, відстежує кількість отриманих пакетів, помилок (невідповідність послідовності або контрольної суми) та обсяг отриманих даних. Виводить статистику в реальному часі (швидкість, кількість пакетів, помилки).
* **Режим Клієнта:** Надсилає UDP-пакети визначеного розміру з певною швидкістю на вказану IP-адресу та порт. Підтримує налаштування MTU та опціональну затримку між пакетами.
* **Послідовність та Контрольна Сума:** Кожен пакет містить порядковий номер та контрольну суму (MD5 від заголовка та даних) для виявлення втрат пакетів та пошкоджень даних.
* **Налаштування MTU:** Дозволяє клієнту вказувати розмір MTU, що впливає на розмір payload'а пакету.
* **Опціональна Затримка:** Можливість додати фіксовану затримку між відправкою пакетів клієнтом.

## Як використовувати

Скрипт запускається з командного рядка. Режим роботи (сервер чи клієнт) визначається наявністю аргументів `-ip` та `-mtu`.

### Режим Сервера

Запустіть скрипт на машині, яка буде приймати трафік. За замовчуванням використовується порт 5005.

```bash
python3 Simple-UDP-Speedtest.py
```

### Режим Клієнта

Запустіть скрипт на машині, яка буде надсилати трафік. Необхідно вказати IP-адресу сервера та MTU.

```bash
python3 Simple-UDP-Speedtest.py -ip 192.168.1.101 -mtu 1400
```


