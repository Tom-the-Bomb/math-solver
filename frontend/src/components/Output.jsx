function Section({name, content}) {
    return (
        <div className="flex flex-col gap-4">
            <h1 className="my-h1">{name}</h1>
            <div className="font-mono p-4 rounded-md bg-rose-800 text-rose-300">
                {content}
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
                <Section name="Simplified" content={response.content.simplified_equation}></Section>
                <Section name="Solution" content={response.content.latex_solution}></Section>
                <Section name="Derivative" content={response.content.derivative}></Section>
            </div>
        )
    } else {
        return ""
    }
}