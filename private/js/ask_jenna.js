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

        el.disabled = true;
        this.extendedLLM(el.name).then((result) => {
            console.log(result);
            el.value = result.content;
            el.disabled = status;
        }).catch(err => {
            console.log(err);
            el.disabled = status;
        });
    }

    async extendedLLM(name) {
        if (this.prompts[name]?.dynamic_content) {
            const response = await fetch(this.prompts[name].dynamic_content);
            const content = await response.text();
            console.log(content);
            return LLM(`Here is HTML content: ${content}\n\n${this.prompts[name].prompt}`, this.options);
        }
        return LLM(this.prompts[name].prompt, this.options);
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