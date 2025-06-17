import { AskJenna } from './ask_jenna';


document.addEventListener('DOMContentLoaded', () => {
    const jenna_config = JSON.parse(document.getElementById('ask_jenna_settings').textContent);
    const jenna_scripts = JSON.parse(document.getElementById('ask_jenna_scripts').textContent);

    const llm = new AskJenna(jenna_config, jenna_scripts);
    for (let field of Object.keys(jenna_scripts)) {
        console.log(field);
        const el = document.querySelector(`input[name="${field}"],textarea[name="${field}"]`);
        if (el) {
            console.log("adding listener");
            el.addEventListener('dblclick', (ev) => {
                console.log("dblClick on ", ev.target.name);
                llm.fill_input(ev.target, jenna_scripts[ev.target.name]?.prompt);
            })
        }
    }
    }
)