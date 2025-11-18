class BasePlugin:
    """Interface yang harus dimiliki semua plugin."""
    NAME = "Plugin Tanpa Nama"
    PHASE = "none" # 'phase1' (requests) or 'phase2_dom' (selenium)

    def __init__(self):
        pass

    def set_context(self, shared_context):
        """Menyuntikkan manajer inti ke dalam plugin."""
        self.result_manager = shared_context["result_manager"]
        self.oast_manager = shared_context.get("oast_manager")
        self.domain = shared_context["domain"]

    def test_vector(self, vector):
        """Fungsi tes Fase 1 (requests)."""
        # 'vector' adalah: (method, url, params_dict)
        raise NotImplementedError

    def test_page(self, driver, url):
        """Fungsi tes Fase 2 (selenium)."""
        raise NotImplementedError