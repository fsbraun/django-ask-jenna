import { AskJenna } from './ask_jenna';

import '../css/admin.css';


document.addEventListener('DOMContentLoaded', () => {
    const jenna_config = JSON.parse(document.getElementById('ask_jenna_settings').textContent);
    const jenna_scripts = JSON.parse(document.getElementById('ask_jenna_scripts').textContent);

    const llm = new AskJenna(jenna_config, jenna_scripts);
    for (let field of Object.keys(jenna_scripts)) {
        console.log(field);
        const el = document.querySelector(`input[name="${field}"]:not([disabled]),textarea[name="${field}"]:not([disabled])`);
        if (el) {
            console.log("adding listener");
            const div = el.closest('div');
            if (div) {
                div.classList.add('ask-jenna-field');
                const wrapper =document.createElement('div');
                wrapper.classList.add('ask-jenna-wrapper');
                const btn = document.createElement('button');
                btn.innerHTML = '<svg><use xlink:href="#icon-ask-jenna"></use></svg>';
                btn.type = 'button';
                wrapper.appendChild(el);
                wrapper.appendChild(btn);
                div.appendChild(wrapper);
                btn.addEventListener('click', (ev) => {
                    console.log("dblClick on ", el.name);
                    llm.fill_input(el);
                });
            }
        }
    }
    }
)