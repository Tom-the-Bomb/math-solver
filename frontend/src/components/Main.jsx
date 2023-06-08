import { useState } from "react";
import { List, Input } from "./List";
import Output from "./Output";

function Textarea({name, required, placeholder, height}) {
    return (
        <textarea
            className={
                `block ${height} w-full resize-none font-serif overflow-y-clip
                my-input text-lg  border-t-2 border-red-900`
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

    return (
        <form className="flex flex-col h-full w-full justify-between" onSubmit={handleSubmit}>
            <div className="flex flex-col gap-10 p-10 overflow-y-auto">
                <List type="Functions"></List>
                <List type="Constants"></List>
                <Input name="solveFor" width="w-1/2" placeholder="Primary variable"></Input>
            </div>
            <div className="h-1/2 w-full self-end inline-block relative">
                <Textarea
                    required={false}
                    name="domain"
                    placeholder={"Domain: e.g. [0, inf)"}
                    height={"h-[15%]"}>
                </Textarea>
                <span class="sr-only">Equation</span>
                <Textarea
                    required={true}
                    name="equation"
                    placeholder={"Enter an equation..."}
                    height={"h-[85%]"}>
                </Textarea>
                <button
                    className="my-focus my-hover text-gray-100 bg-green-500
                    rounded-lg p-3 absolute bottom-[5%] right-8"
                    type="submit"
                >Enter</button>
            </div>
        </form>
    )
}

export default function Main({host}) {
    const [ response, setResponse ] = useState(null);

    return (
        <main className="grow grid grid-cols-2 flex-wrap">
            <div className="bg-red-1 drop-shadow-2xl">
                <Form setResponse={(x) => setResponse(x)} host={host}></Form>
            </div>
            <div className="bg-red-2 p-10">
                <h1 className="my-h1">Output</h1>
                <Output response={response}></Output>
            </div>
        </main>
    )
}