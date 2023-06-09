import { useState, useEffect, useRef } from "react";
import { List, Input } from "./List";
import Output from "./Output";
import { MathJax } from "better-react-mathjax";

function Textarea({onChange, name, required, placeholder, height}) {
    return (
        <textarea
            onChange={onChange}
            className={
                `scrollbar-gray block ${height} w-full resize-none font-serif overflow-y-auto
                my-input text-lg border-t-2 border-red-900`
            }
            placeholder={placeholder}
            type="text"
            name={name}
            required={required}
            spellCheck="false"
            autoCorrect="false"
            autoCapitalize="false"
            data-gramm="false" data-gramm_editor="false" data-enable-grammarly="false"
        />
    )
}

function Form({host, setResponse}) {
    async function handleSubmit(event) {
        event.preventDefault();

        const elements = event.target.elements;
        const domain = elements.domain.value || null;
        const solveFor = elements.solveFor.value || null;
        const equation = elements.equation.value;

        const elementList = Array.from(elements);
        const functions = elementList
            .filter(x => x.classList.contains("a-function") && x.value)
            .map(x => x.value);
        const constants = Object.fromEntries(
            elementList
                .filter(x => x.classList.contains("constant-name") && x.value)
                .map(x => [x.value, elementList[elementList.indexOf(x) + 1].value || 0])
        );

        try {
            const response = await fetch(
                `${host}/solve`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        'equation': equation,
                        'domain': domain,
                        'solve_for': solveFor,
                        'functions': functions,
                        'constants': constants,
                    }),
                }
            );

            const raw = await response.text();
            let content;
            try {
                content = JSON.parse(raw);
            } catch {
                let message;
                switch (response.status) {
                    case 429:
                        message = "To many requests... Slow down!";
                        break;
                    case 400:
                        message = "Bad Input data... :/";
                        break;
                    case 500:
                        message = "Something went wrong... :(";
                        break;
                    default:
                        message = raw;
                }
                content = {
                    error: message
                };
            }

            setResponse({
                status: response.status,
                ok: response.ok,
                content: content,
            });
        } catch(e) {
            setResponse({
                status: 0,
                ok: false,
                content: {
                    error: e.message,
                },
            });
        }
    }

    const [ rendered, setRendered ] = useState(null);
    return (
        <form className="flex flex-col h-full w-full justify-between" onSubmit={handleSubmit}>
            <div className="scrollbar-red flex flex-col gap-10 h-1/2 pt-5 p-10 overflow-y-auto">
                <List type="Functions"></List>
                <List type="Constants"></List>
                <Input name="solveFor" width="w-1/2" placeholder="Isolate for :"></Input>
            </div>
            <div className="h-1/2 w-full self-end inline-block relative">
                <Textarea
                    required={false}
                    name="domain"
                    placeholder="Domain: e.g. [0, inf)"
                    height="h-[15%]">
                </Textarea>
                <span class="sr-only">Equation</span>
                <div className="flex flex-col h-[85%]">
                    <MathJax className="border-t-2 border-red-900 my-input">
                        {rendered
                            ? rendered
                            : <div className="text-slate-400 font-math italic">Latex equation</div>
                        }
                    </MathJax>
                    <Textarea
                        onChange={(e) => setRendered(e.target.value ? "`" + e.target.value + "`" : null)}
                        required={true}
                        name="equation"
                        placeholder="Enter an equation..."
                        height="grow">
                    </Textarea>
                </div>
                <button
                    className="my-focus my-hover text-gray-100 bg-green-500
                    rounded-lg p-3 absolute bottom-[5%] right-8"
                    type="submit"
                >Solve</button>
            </div>
        </form>
    )
}

export default function Main({host}) {
    const [ response, setResponse ] = useState(null);

    return (
        <main className="flex flex-row flex-wrap grow">
            <div className="bg-red-1 lg:w-1/2 grow drop-shadow-2xl">
                <Form setResponse={(x) => setResponse(x)} host={host}></Form>
            </div>
            <div className="bg-red-2 lg:w-1/2 grow p-10">
                <h1 className="text-4xl my-h1">Output</h1>
                <Output response={response}></Output>
            </div>
        </main>
    )
}