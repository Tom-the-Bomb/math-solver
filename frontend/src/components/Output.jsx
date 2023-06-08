import { useRef, useEffect } from "react";

var katex = require('katex');

function Latex({content}) {
    const container = useRef();

    useEffect(() => {
        katex.render(content, container.current);
    }, [content]);

    return <div ref={container} />
}

function Section({latex, name, content}) {
    return (
        <div className="flex flex-col gap-4">
            <h1 className="my-h1">{name}</h1>
            <div className="font-mono p-4 rounded-md bg-rose-800 text-rose-300">
                {latex ? <Latex content={content}></Latex> : content}
            </div>
        </div>
    )
}

export default function Output({response}) {
    if (response) {
        if (!response.ok) {
            return (
                <div className="mt-10">
                    <Section name="Error" content={response.content.error}></Section>
                </div>
            )
        }
        return (
            <div className="mt-10">
                <Section latex={true} name="Simplified" content={response.content.simplified_equation}></Section>
                <Section latex={true} name="Solution" content={response.content.latex_solution}></Section>
                <Section latex={true} name="Derivative" content={response.content.derivative}></Section>
            </div>
        )
    } else {
        return (
            <p className="text-rose-300 text-2xl mt-10 bold">Enter some math first...</p>
        )
    }
}