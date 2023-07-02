class Transaction:
    def __init__(self, **kwargs) -> None:
        self.transaction_id = kwargs["transaction_id"]
        self.payment_method = kwargs["payment_method"]
        self.take_process = kwargs["take_process"]
        self.give_process = kwargs["give_process"]
        self.status = kwargs["status"]
        self.payment_system_status = kwargs["payment_system_status"]
        self.diagnose = kwargs["diagnose"]
        if "register_time" in kwargs:
            self.register_time = kwargs["register_time"]
        if "funds_credited_time" in kwargs:
            self.funds_credited_time = kwargs["funds_credited_time"]
        if "funds_sent_time" in kwargs:
            self.funds_sent_time = kwargs["funds_sent_time"]
        if "move_to_bo_time" in kwargs:
            self.move_to_bo_time = kwargs["move_to_bo_time"]
        if "processing_time_in_seconds" in kwargs:
            self.processing_time_in_seconds = kwargs["processing_time_in_seconds"]
        if "waiting_bo_time_in_seconds" in kwargs:
            self.waiting_bo_time_in_seconds = kwargs["waiting_bo_time_in_seconds"]
        if "card_issuer_country_code" in kwargs:
            self.source_country = kwargs["source_country"]
        if "resident_country" in kwargs:
            self.resident_country = kwargs["resident_country"]
        if "card_issuer_country_name" in kwargs:
            self.card_issuer_country_name = kwargs["card_issuer_country_name"]
        if "country_alpha2" in kwargs:
            self.country_alpha2 = kwargs["country_alpha2"]
        if "doc_req_over_24h" in kwargs:
            self.doc_req_over_24h = kwargs.get("doc_req_over_24h")
        if "blacklist" in kwargs:
            self.blacklist = kwargs.get("blacklist")
        if "sla_violation" in kwargs:
            self.sla_violation = kwargs.get("sla_violation")
        if "ip_violation" in kwargs:
            self.ip_violation = kwargs.get("ip_violation")
        if "action" in kwargs:
            self.action = kwargs.get("action")
        if "action_done" in kwargs:
            self.action_done = kwargs.get("action_done")
