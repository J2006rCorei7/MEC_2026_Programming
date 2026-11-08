app = None
db = None
RequestModel = None


def set_model(app_instance, db_instance, model):
    global app, db, RequestModel

    app = app_instance
    db = db_instance
    RequestModel = model


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
    with app.app_context():
        request = db.session.get(RequestModel, request_id)

        if request is None:
            return False

        db.session.delete(request)
        db.session.commit()

        return True