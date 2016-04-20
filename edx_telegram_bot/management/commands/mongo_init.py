# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from ...bot_mongo import BotMongo

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('course_name', nargs='+', type=str)

    def handle(self, *args, **options):
        self.course_key = options['course_name'][0]
        self.mongo_client = BotMongo(database='bot', collection=self.course_key)
        #  Initial fixtures for mongo collection
        # Introduction step
        self.mongo_client.send({'Problem': """
*Помоги Еноту Петру в реформировании собственного зоопарка*
Енот Петр был одним из жителей Зоопарка “Межлисся”. Он стал вожаком животных после бегства Кабана Виктора. Парой месяцев до того лидер хряков бежал в соседний зоопарк “Северный Писец” из-за того что зажрался.
Зоопарк был в плачевном состоянии. При побеге, Виктор вынес практически все запасы сьестного, прихватив южную часть угодий.
                                            """,
                               'Right_answer': "Я готов!",
                               'Wrong_answers': [],
                               'Image_url': 'https://s-media-cache-ak0.pinimg.com/736x/a7/54/e7/a754e7ff082fb93173f42f0ff5a4b15d.jpg',
                               'Positive_answer': "*Ты просто мой герой, тогда вперед.*",
                               'Order': 0,
                               'Next_step_order': 1})
        # Step 1
        self.mongo_client.send({'Problem': '''
Петр предложил свою кандидатуру на пост вожака. Он объяснял это тем, что нет животного в зоопарке, способного запустить маховик реформ.
***Как считаешь, способны ли Еноты на осмысленные действия? Хватит ли ума у Енота на проведения реформ?***
                                            ''',
                                'Wrong_answers': ['Конечно нет, все еноты тупые', 'Енот может воровать еду и не более'],
                                'Right_answer': 'На самом деле они очень умные создания',
                                'Theoretical_part': '''
high IQ level of raccoons is one of the most amazing raccoon facts in this list. According to experts, raccoons scored very high on the mammal IQ level test. They are found to be more intelligent than cats. They have amazing skills of opening locks and close doors. In a study, in total of 13 locks, raccoons were able to open 11 locks. They were also able to memorize the combination which suggests raccoons were intelligent enough to understand the complex mechanism of locks. Raccoons have amazing and quick learning skills. They can memorize the solution of complex mechanism for three years and they can also identify and differentiate between different symbols.
Moreover, Smartest raccoons (IQ higher than average monkey has ) work in Raccoon Gang :D
                                            ''',
                                'Negative_answer': "Зря ты так про енотов, я ведь знаю твой Telegram ID. Лучше попробуй еще раз.",
                                'Positive_answer': "*Точно, еноты лучшие, поэтому у него все выйдет*",
                                'Order': 1,
                                'Next_step_order': 2})
        # Step 2
        self.mongo_client.send({'Problem': '''
Посовещавшись, животные дали ему мандат доверия на столько лет, сколько пальцев у него было на лапе.
***Как думаешь сколько у енота пальцев на лапе?***
                                            ''',
                                'Wrong_answers': ['Один палец', 'Два больших и один маленький', '4 пальца'],
                                'Right_answer': '5 пальцев',
                                'Theoretical_part': "A raccoon’s hands are so nimble they can unlace a shoe, unlatch a cage and deftly retrieve coins as thin as dimes from your shirt pocket.",
                                'Negative_answer': "На самом деле еноты гораздо сильнее похожи на людей, чем ты думауешь, давай еще раз попробуем.",
                                'Positive_answer': "Не стоит так радоваться. Это было просто. ;)",
                                'Order': 2,
                                'Next_step_order': 3})
        # Step 3
        self.mongo_client.send({'Problem': '''
Петру начали помогать многие его друзья, одним из которы был Кролик Сеня. Сеня очень любил морковку. Морковки в государстве было мало, а собственные грядки были разорены сбегавшими Кабаном Виктором и стадом его прихвостней. Было решено взять морковки взаймы у соседних зоопарков. Но разве одной морковкой поможешь?
*Кстати, а что вообще едят еонты?*
                                            ''',
                                'Wrong_answers': ['Пьют пиво и едят чипсы', 'Пьют пиво и едят мясо', 'Пицца и бургеры'],
                                'Right_answer': 'Что-то другое',
                                'Theoretical_part': "A raccoon’s hands are so nimble they can unlace a shoe, unlatch a cage and deftly retrieve coins as thin as dimes from your shirt pocket.",
                                'Negative_answer': "Сам это ешь, еноты не настолько тупые.",
                                'Positive_answer': "О да, я це люблю, давайте мне больше такой еды.",
                                'Order': 3,
                                'Next_step_order': 4})
        # Step 4
        self.mongo_client.send({'Problem': '''
Пронырливые сороки выяснили, что Енот Петр бегал в соседний зоопарк, чтобы мыть там морковь. Предположительно, Петр мыл ее там, ибо вода в пруду мутная и не видно сколько моркови оседает на дне. Несмотря на то, что все это держалось в строгой тайне, попался не только он, но и руководитель «Северного Песца» - Пудель Вова.
*А ты как думаешь, вправду ли Еноты полощат еду?*
                                    ''',
                                'Wrong_answers': ['Всегда полощат перед едой', 'Полощат только грязную еду'],
                                'Right_answer': 'Ничего они не полощат, это все клевета',
                                'Theoretical_part': 'They are true omnivores and are opportunistic in their diet. They will eat fruit, insects, berries, nuts, eggs, small rodents, grapes, corn, crabs, crayfish and anything edible you may have left in the backyard. It was once thought that raccoons washed their food. They do not. Raccoons have a highly sensitive sense of touch which water helps to enhance. Even when water is unavailable, raccoons will use the same motions while they manipulate their food or objects they are interested in. This tactile experience gives the raccoon a better sense of what it will be eating. It is as if they "see" with their hands.Raccoons have bad eyesight and are color blind, but have great hearing and a great sense of smell.',
                                'Negative_answer': "Ожидаемо, все так думают, но это неправда",
                                'Positive_answer': "Красавчик, вижу ты смотришь Animal Planet",
                                'Order': 4,
                                'Next_step_order': 5})
        # Step 5
        self.mongo_client.send({'Problem': '''
Звери начали постепенно разочаровываться в Петре. Хватит ли времени у Енота, чтобы навести порядок в зоопарке?
*Сколько Еноты обычно живут?*
                                    ''',
                                'Wrong_answers': ['Меньше 5 лет', 'До 10 лет', 'До 15 лет'],
                                'Right_answer': 'Более 15 лет',
                                'Theoretical_part': 'They are true omnivores and are opportunistic in their diet. They will eat fruit, insects, berries, nuts, eggs, small rodents, grapes, corn, crabs, crayfish and anything edible you may have left in the backyard. It was once thought that raccoons washed their food. They do not. Raccoons have a highly sensitive sense of touch which water helps to enhance. Even when water is unavailable, raccoons will use the same motions while they manipulate their food or objects they are interested in. This tactile experience gives the raccoon a better sense of what it will be eating. It is as if they "see" with their hands.Raccoons have bad eyesight and are color blind, but have great hearing and a great sense of smell.',
                                'Negative_answer': "Ты их недооцениваешь, Петр еще успеет простудиться на твоих похоронах",
                                'Positive_answer': "Красавчик, вижу ты смотришь Animal Planet",
                                'Order': 5,
                                })
