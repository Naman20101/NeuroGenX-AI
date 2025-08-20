from app.core.registry import save_champion

class DeployFastAPI:
    name="deploy_fastapi"; version="0.1"
    def run(self, ctx):
        man = save_champion(ctx["run_id"], ctx["fitted_pipeline"].named_steps["pre"],
                            ctx["fitted_pipeline"].named_steps["clf"], ctx["metrics"])
        ctx["manifest"] = man
        return ctx