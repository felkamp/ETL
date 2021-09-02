# Проектное задание: ETL

В предыдущем модуле вы реализовывали механизм для полнотекстового поиска. Теперь улучшим его: научим его работать с новой схемой и оптимизируем количество элементов для обновления.

## Подсказки

Перед тем как вы приступите к выполнению задания, дадим несколько подсказок:

1. Прежде чем выполнять задание, подумайте, сколько ETL-процессов вам нужно.
2. Для валидации конфига советуем использовать pydantic.
3. Для построения ETL-процесса используйте корутины.
4. Чтобы спокойно переживать падения Postgres или Elasticsearch, используйте решение с техникой `backoff` или попробуйте использовать одноимённую библиотеку.
5. Ваше приложение должно уметь восстанавливать контекст и начинать читать с того места, где оно закончило свою работу.
6. При конфигурировании ETL-процесса подумайте, какие параметры нужны для запуска приложения. Старайтесь оставлять в коде как можно меньше «магических» значений.
7. Желательно, но необязательно сделать составление запросов в БД максимально обобщённым, чтобы не пришлось постоянно дублировать код. При обобщении не забывайте о том, что все передаваемые значения в запросах должны экранироваться.
8. Использование тайпингов поможет сократить время дебага и повысить понимание кода ревьюерами, а значит работы будут проверяться быстрее :)
9. Обязательно пишите, что делают функции в коде.
10. Для логирования используйте модуль `logging` из стандартной библиотеки Python.

Желаем вам удачи в написании ETL! Вы обязательно справитесь 💪 

**Решение задачи залейте в папку `postgres_to_es` вашего репозитория.**