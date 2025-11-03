from pathlib import Path
from bs4 import BeautifulSoup
import textwrap

files_data = {
    'intro/about/\u8bb8\u53cc\u535a.html': {
        'title_en': 'Xu Shuangbo · Personal Profile',
        'title_zh': '许双博 · 个人介绍',
        'name_en': 'Xu Shuangbo',
        'name_zh': '许双博',
        'subtitle_en': 'Product Coordinator · Homepage Experience Lead',
        'subtitle_zh': '产品统筹 · 主页体验负责人',
        'back_en': 'Back',
        'back_zh': '返回',
        'button_en': 'Reveal the easter egg',
        'button_zh': '点我查看隐藏真相',
        'cards': {
            '基本介绍': {
                'heading_en': 'Profile Summary',
                'english_html': '''
                    <p>I am a second-year Data Science and Big Data Technology student at Beijing Institute of Technology. Inside the movie recommendation project I coordinate the product work, synchronise delivery across four scoring teammates, and translate requirements into user-facing experiences. Daytime is for requirement specs; nights are reserved for README updates and deployment notes.</p>
                '''
            },
            '专业技能': {
                'heading_en': 'Core Skills',
                'english_html': '''
                    <ul>
                        <li><strong>Interaction prototyping:</strong> Validate recommendation layouts quickly in Figma or on a whiteboard.</li>
                        <li><strong>Front-end integration:</strong> Maintain the `intro/about` and homepage assets so paths, fonts, and build scripts stay aligned.</li>
                        <li><strong>Progress tracking:</strong> Drive the Notion kanban to mirror every scoring script’s test status and chase missing logs on time.</li>
                        <li><strong>Data literacy:</strong> Translate model metrics into language such as "recommendations are getting sharper."</li>
                    </ul>
                '''
            },
            '项目贡献': {
                'heading_en': 'Project Contributions',
                'english_html': '''
                    <ul>
                        <li>Built the static landing site and reporting pages, and curated the navigation plus color system.</li>
                        <li>Standardised data-file naming so everything in <code>reports/</code> remains traceable.</li>
                        <li>Prepared presentation assets by breaking complex algorithm flows into three diagrams and one story.</li>
                        <li>Jumped on environment failures immediately to pair-debug with engineers until the demo ran.</li>
                    </ul>
                '''
            },
            '个人特色': {
                'heading_en': 'Personal Traits',
                'english_html': '''
                    <ul>
                        <li><strong>User empathy:</strong> Evaluate each recommendation from a cinephile’s perspective.</li>
                        <li><strong>Inspiration hunter:</strong> Dissects media apps and collects interaction ideas worth reusing.</li>
                        <li><strong>Resilient under pressure:</strong> Can pull late-night shifts and still brief progress with a smile the next morning.</li>
                        <li><strong>Hidden talent:</strong> Turns messy meeting notes into a clear action checklist within minutes.</li>
                    </ul>
                '''
            },
            '成长经历': {
                'heading_en': 'Growth Journey',
                'english_html': '''
                    <p>Started by simply pushing CSV files into a web page, and can now assemble a full showcase site. Learned to collaborate across algorithm, data, and design roles. Next milestone: finish a front-end testing routine so every go-live lands on a predictable cadence.</p>
                '''
            },
            '未来目标': {
                'heading_en': 'Future Goals',
                'english_html': '''
                    <p>Plan to package the recommendation system into a reusable product template, giving other teams a repeatable data → model → presentation pipeline. Will also route user feedback back into the data stack to build a truly audience-centered loop.</p>
                '''
            },
            '座右铭': {
                'heading_en': 'Motto',
                'english_html': '''
                    <blockquote>
                        <p>“Ship dates belong on the calendar; experiences belong in users’ hearts.”</p>
                        <p>“A project only launches once the documentation is finished.”</p>
                    </blockquote>
                '''
            },
            '联系方式': {
                'heading_en': 'Contact',
                'english_html': '''
                    <p>Email: <a href="mailto:shuangboxu2@gmail.com">shuangboxu2@gmail.com</a></p>
                '''
            }
        }
    },
    'intro/about/\u738b\u97f5\u5609.html': {
        'title_en': 'Wang Yunjia · Content Intelligence',
        'title_zh': '王韵嘉 · 内容理解',
        'name_en': 'Wang Yunjia',
        'name_zh': '王韵嘉',
        'subtitle_en': 'Narrative Analyst · Content Scoring',
        'subtitle_zh': '文本感知 · 内容评分',
        'back_en': 'Back',
        'back_zh': '返回',
        'button_en': 'Toggle the easter egg',
        'button_zh': '点我查看隐藏真相',
        'cards': {
            '角色与职责': {
                'heading_en': 'Role & Responsibilities',
                'english_html': '''
                    <p>Owns the content understanding module of the movie recommender. Builds natural-language features from reviews, plot summaries, and awards to design emotion and narrative-completeness scores that explain the final rating. Maintains <code>scripts/02_text_scores.py</code> with runnable docs and unit tests so every scoring run is reproducible.</p>
                '''
            },
            '学习方向': {
                'heading_en': 'Learning Focus',
                'english_html': '''
                    <p>Deepens expertise in NLP and information retrieval, comfortable with fine-tuning Transformer models while exploring how BM25 and sparse vectors combine for review search. Curates Douban and Rotten Tomatoes corpora, loves crafting prompt-generated tag clouds to inspire teammates.</p>
                '''
            },
            '兴趣爱好': {
                'heading_en': 'Interests',
                'english_html': '''
                    <p>Obsessed with film festivals, red-carpet lore, and post-credit trivia; weekends are for live-blogging screening notes. Also reverse-engineers playlist logic at TGI Friday, and occasionally hosts podcasts to share tips on scoring models so data can tell human stories.</p>
                '''
            },
            '未来展望': {
                'heading_en': 'Future Outlook',
                'english_html': '''
                    <p>Plans to blend text scoring with a knowledge graph and build a “director style vector” lab. The goal is to explain recommendation results with “why this film” narratives instead of “because the model said so.”</p>
                '''
            }
        }
    },
    'intro/about/\u6b66\u7ea2\u73ae.html': {
        'title_en': 'Wu Hongwei · User Research',
        'title_zh': '武红玮 · 用户研究',
        'name_en': 'Wu Hongwei',
        'name_zh': '武红玮',
        'subtitle_en': 'User Research · Project Journal',
        'subtitle_zh': '用户研究 · 项目记录',
        'back_en': 'Back',
        'back_zh': '返回',
        'button_en': 'Reveal the easter egg',
        'button_zh': '点我查看隐藏真相',
        'cards': {
            '基本概况': {
                'heading_en': 'Profile',
                'english_html': '''
                    <p>First-year Data Science and Big Data Technology student who loves finding stories in the details. In the movie recommendation project I capture user insights and keep the project journal, acting as both the team’s recorder and active listener.</p>
                '''
            },
            '项目角色': {
                'heading_en': 'Project Role',
                'english_html': '''
                    <p>Runs surveys and interviews to map viewing preferences, acceptable recommendation cadence, and presentation styles, turning “users’ voices” into an actionable requirement sheet. Also maintains <code>reports/logs/</code> to document each scoring iteration, merge strategy, and issue list so the team can backtrack anytime.</p>
                '''
            },
            '兴趣与探索': {
                'heading_en': 'Interests & Exploration',
                'english_html': '''
                    <p>Enjoys reading reviews and long-form posts on Douban, and writes short essays about everyday viewing experiences. Fascinated by information architecture and layout; currently learning how Markdown plus Obsidian can build a knowledge base to preserve user-research methods.</p>
                '''
            },
            '未来期待': {
                'heading_en': 'Looking Ahead',
                'english_html': '''
                    <p>Wants the recommendation system to feel closer to real audiences—so that every suggestion feels “made for me.” Next step is to feed research findings back into feature engineering so qualitative warmth becomes measurable data.</p>
                '''
            }
        }
    }
}

def set_bilingual(soup, element, en_text, zh_text, prefix=None):
    element.clear()
    if prefix:
        element.append(soup.new_string(prefix))
    span_en = soup.new_tag('span', attrs={'class': 'lang-en'})
    span_en.string = en_text
    span_zh = soup.new_tag('span', attrs={'class': 'lang-zh'})
    span_zh.string = zh_text
    element.append(span_en)
    element.append(soup.new_string(' '))
    element.append(span_zh)

for path, cfg in files_data.items():
    file_path = Path(path)
    soup = BeautifulSoup(file_path.read_text(encoding='utf-8'), 'html.parser')

    soup.title.string = f"{cfg['title_en']} | {cfg['title_zh']}"

    profile = soup.select_one('.profile')
    set_bilingual(soup, profile.find('h1'), cfg['name_en'], cfg['name_zh'])
    set_bilingual(soup, profile.find('h3'), cfg['subtitle_en'], cfg['subtitle_zh'])

    back_link = soup.select_one('a.back')
    set_bilingual(soup, back_link, cfg['back_en'], cfg['back_zh'], prefix='← ')

    button = soup.select_one('button.easter')
    if button:
        set_bilingual(soup, button, cfg['button_en'], cfg['button_zh'])

    for card in soup.select('div.card'):
        heading = card.find('h2').get_text(strip=True)
        if heading not in cfg['cards']:
            continue
        info = cfg['cards'][heading]
        set_bilingual(soup, card.find('h2'), info['heading_en'], heading)

        zh_wrapper = soup.new_tag('div', attrs={'class': 'lang-zh'})
        children = []
        for child in list(card.children):
            if getattr(child, 'name', None) and child.name != 'h2':
                children.append(child)
        for child in children:
            zh_wrapper.append(child.extract())

        en_wrapper = soup.new_tag('div', attrs={'class': 'lang-en'})
        en_fragment = BeautifulSoup(textwrap.dedent(info['english_html']).strip(), 'html.parser')
        for node in en_fragment.contents:
            en_wrapper.append(node)

        card.append(en_wrapper)
        card.append(zh_wrapper)

    file_path.write_text(soup.prettify(formatter='html'), encoding='utf-8')
