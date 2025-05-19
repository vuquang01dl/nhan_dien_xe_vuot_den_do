def sort_ocr_boxes(results, model):
    chars = []
    for *xyxy, conf, cls in results.xyxy[0]:
        x1, y1, x2, y2 = map(int, xyxy)
        x_center = (x1 + x2) // 2
        y_center = (y1 + y2) // 2
        chars.append({
            'char': model.names[int(cls)],
            'x': x_center,
            'y': y_center
        })

    chars.sort(key=lambda c: (c['y'] // 15, c['x']))
    return ''.join([c['char'] for c in chars])
