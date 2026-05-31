import { router } from "./router.js";

window.addEventListener("hashchange", router);
router();
