export type Form = {
    automatic_response_id: string
    examples: string[]
    name: string
    org_code: string
    response: string
}

export enum FormKeys {
    automatic_response_id = 'ID',
    examples = 'ejemplos',
    name = 'nombre',
    response = 'respuesta',
}
