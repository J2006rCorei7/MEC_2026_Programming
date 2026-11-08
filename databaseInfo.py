from main import app, db, RequestModel, Person

def get_all_requests():
    with app.app_context():
        requests = RequestModel.query.all()
        return [r.to_dict() for r in requests]


def get_request_by_id(request_id):
    with app.app_context():
        request = db.session.get(RequestModel, request_id)

        if request is None:
            return None

        return request.to_dict()

def update_request(request_id, updates):
    with app.app_context():
        request = db.session.get(RequestModel, request_id)

        if request is None:
            return False

        allowed_fields = [
            "dest_name",
            "dest_type",
            "num_people",
            "address",
            "hot_food_needed",
            "hot_food_available",
            "cold_food_needed",
            "cold_food_available",
            "delivery_deadline",
            "urgency_level"
        ]

        for field, value in updates.items():
            if field in allowed_fields:
                setattr(request, field, value)

        db.session.commit()
        return True

def delete_request(request_id):
    request = db.session.get(RequestModel, request_id)

    if request is None:
        return False

    db.session.delete(request)
    db.session.commit()

    return True

if __name__ == '__main__':
    print(get_all_requests())
    update_request(1, {"urgency_level": "moderate", "hot_food_available": 10, "num_people": 15})
    print(get_all_requests())