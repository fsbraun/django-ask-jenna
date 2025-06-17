import LLM from '@themaximalist/llm.js'

class AskJenna {
    constructor(options, prompts) {
        this.options = options;
        this.prompts = prompts;
    }

    fill_input(el) {
        if (!this.prompts[el.name]) {
            return;
        }
        const status = el.disabled;
        const previousValue = el.value;
        el.value = '';  // Clear the input field
        el.disabled = true;  // Disable the input field to prevent changes while processing
        this.extendedLLM(el.name).then((result) => {
            console.log(result);
            el.value = this.deconstructJson(result);
            el.disabled = status;
        }).catch(err => {
            el.value = previousValue;  // Restore previous value on error
            el.disabled = status;  // Restore previous disabled state
            console.error(err);
        });
    }

    deconstructJson(json) {
        if (typeof json == 'string') {
            return json;
        }
        if (typeof json == 'object' && Object.keys(json).length === 1) {
            const key = Object.keys(json)[0];
            return this.deconstructJson(json[key]);
        }
        if (Array.isArray(json) && json.length === 1) {
            return this.deconstructJson(json[0]);
        }
        return json;
    }

    async extendedLLM(name) {
        if (this.prompts[name]?.dynamic_content) {
            const response = await fetch(this.prompts[name].dynamic_content);
            const div = document.createElement('div');
            div.innerHTML = await response.text();
            const nodeToRemove = div.querySelector('div#cms-top');
            if (nodeToRemove) {
                nodeToRemove.remove();
            }
            div.querySelectorAll('meta, style, script, template, nav').forEach(node => node.remove());
            const content = this.htmlToMDContent(div);
            return LLM(`Here is HTML content: ${content}\n\n${this.prompts[name].prompt}`, this.options);
        }
        return LLM(this.prompts[name].prompt, this.options);
    }

    htmlToMDContent (element) {
        function traverse(node) {
            if (node.nodeType === Node.TEXT_NODE) {
            return node.textContent;
            }
            if (node.nodeType !== Node.ELEMENT_NODE) {
            return '';
            }
            let md = '';
            switch (node.tagName.toLowerCase()) {
            case 'h1':
                md += '# ' + Array.from(node.childNodes).map(traverse).join('').trim() + '\n\n';
                break;
            case 'h2':
                md += '## ' + Array.from(node.childNodes).map(traverse).join('').trim() + '\n\n';
                break;
            case 'h3':
                md += '### ' + Array.from(node.childNodes).map(traverse).join('').trim() + '\n\n';
                break;
            case 'h4':
                md += '#### ' + Array.from(node.childNodes).map(traverse).join('').trim() + '\n\n';
                break;
            case 'h5':
                md += '##### ' + Array.from(node.childNodes).map(traverse).join('').trim() + '\n\n';
                break;
            case 'h6':
                md += '###### ' + Array.from(node.childNodes).map(traverse).join('').trim() + '\n\n';
                break;
            case 'strong':
            case 'b':
                md += '**' + Array.from(node.childNodes).map(traverse).join('') + '**';
                break;
            case 'em':
            case 'i':
                md += '*' + Array.from(node.childNodes).map(traverse).join('') + '*';
                break;
            case 'code':
                md += '`' + Array.from(node.childNodes).map(traverse).join('') + '`';
                break;
            case 'pre':
                md += '```\n' + Array.from(node.childNodes).map(traverse).join('') + '\n```\n\n';
                break;
            case 'ul':
                md += Array.from(node.children).map(li => '- ' + traverse(li).trim()).join('\n') + '\n\n';
                break;
            case 'ol':
                md += Array.from(node.children).map((li, i) => `${i + 1}. ${traverse(li).trim()}`).join('\n') + '\n\n';
                break;
            case 'li':
                md += Array.from(node.childNodes).map(traverse).join('');
                break;
            case 'a':
                const href = node.getAttribute('href') || '';
                md += `[${Array.from(node.childNodes).map(traverse).join('')}](${href})`;
                break;
            case 'img':
                const alt = node.getAttribute('alt') || '';
                const src = node.getAttribute('src') || '';
                md += `![${alt}](${src})`;
                break;
            case 'blockquote':
                md += '> ' + Array.from(node.childNodes).map(traverse).join('').replace(/\n/g, '\n> ') + '\n\n';
                break;
            case 'br':
                md += '  \n';
                break;
            case 'p':
                md += Array.from(node.childNodes).map(traverse).join('').trim() + '\n\n';
                break;
            default:
                md += Array.from(node.childNodes).map(traverse).join('');
            }
            return md;
        }
        return traverse(element).replace(/\n{3,}/g, '\n\n').trim();
    }

    async ask(question) {
        try {
            const response = await this.llm.chat({
                messages: [
                    { role: "system", content: "You are Jenna, a helpful assistant." },
                    { role: "user", content: question }
                ]
            });
            return response.choices[0].message.content;
        } catch (error) {
            console.error("Error asking Jenna:", error);
            throw new Error("Failed to get a response from Jenna.");
        }
    }
}

export { AskJenna };