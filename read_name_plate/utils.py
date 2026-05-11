from ultralytics import YOLO
from paddleocr import PaddleOCR
import os
import cv2


def read_name_plate(image_path):
    # 1. Initialisation une seule fois (hors boucle)
    print(image_path)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, 'best.pt')
    model = YOLO(model_path)
    ocr = PaddleOCR(lang='fr', use_angle_cls=True, use_gpu=True,
                    det_db_thresh=0.2,           # Plus sensible pour petits textes techniques
                    det_db_box_thresh=0.4,       # Garde plus de zones candidates
                    det_db_unclip_ratio=1.8,     # Boîtes un peu plus larges pour les chiffres
                    rec_batch_num=6,             # Traitement par lot standard
                    # Pour les longues références (01351CVTIR03)
                    max_text_length=50,
                    # Préserver les espaces (CAHORS TRANSFIX)
                    use_space_char=True,
                    drop_score=0.3,              # Garde même les lectures moyennement confiantes
                    )

    # 2. Charger la nouvelle photo de plaque
    # photo_path = os.path.join(current_dir, './IMG-20250308-WA0000.jpg')
    photo_path = image_path
    img = cv2.imread(photo_path)
    resultats_detection = model(img)[0]

    informations = {}

    identified_nom_classes = []
    # 3. Pour chaque zone détectée
    for boite in resultats_detection.boxes:
        # Récupérer les coordonnées de la zone
        x1, y1, x2, y2 = map(int, boite.xyxy[0])
        classe_id = int(boite.cls[0])
        nom_classe = model.names[classe_id]

        # Découper la zone (reste en BGR, format natif PaddleOCR)
        zone_image = img[y1:y2, x1:x2]

        # 4. Lire le texte avec PaddleOCR (reconnaissance seule, pas de détection)
        resultat = ocr.ocr(zone_image, det=False, cls=False)

        # Extraire et nettoyer le texte
        if not nom_classe in identified_nom_classes:
            identified_nom_classes.append(nom_classe)
            texte = ''
            if resultat and resultat[0]:
                for ligne in resultat[0]:
                    texte += ligne[0] + ' '

            texte = texte.strip()

            # Stocker le résultat
            informations[nom_classe] = texte
            print(f"{nom_classe}: {texte}")

    return informations


# read_name_plate('./IMG-20250308-WA0000.jpg')
