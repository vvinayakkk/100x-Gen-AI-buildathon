# memes/meme_templates.py

class MemeTemplate:
    def __init__(self, name: str, box_count: int, template_id: str):
        self.name = name
        self.box_count = box_count
        self.template_id = template_id

templates = {
    'Drake Hotline Bling': MemeTemplate('Drake Hotline Bling', 2, '181913649'),
    'Two Buttons': MemeTemplate('Two Buttons', 3, '87743020'),
    'Left Exit 12 Off Ramp': MemeTemplate('Left Exit 12 Off Ramp', 3, '124822590'),
    'Disaster Girl': MemeTemplate('Disaster Girl', 2, '97984'),
    'Epic Handshake': MemeTemplate('Epic Handshake', 3, '135256802'),
    "Gru's Plan": MemeTemplate("Gru's Plan", 4, '131940431'),
    'Always Has Been': MemeTemplate('Always Has Been', 2, '252600902'),
    'Sad Pablo Escobar': MemeTemplate('Sad Pablo Escobar', 3, '80707627'),
    'Batman Slapping Robin': MemeTemplate('Batman Slapping Robin', 2, '438680'),
    'Waiting Skeleton': MemeTemplate('Waiting Skeleton', 2, '4087833'),
    'Anakin Padme 4 Panel': MemeTemplate('Anakin Padme 4 Panel', 3, '322841258'),
    'Woman Yelling At Cat': MemeTemplate('Woman Yelling At Cat', 2, '188390779'),
    'Buff Doge vs. Cheems': MemeTemplate('Buff Doge vs. Cheems', 4, '247375501'),
}