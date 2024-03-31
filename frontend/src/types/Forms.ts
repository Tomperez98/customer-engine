export type Form = {
    automatic_response_id: string
    name: string
    org_code: string
    response: string
}

export enum FormKeys {
    automatic_response_id = 'ID',
    name = 'nombre',
    response = 'respuesta',
}

export type FormKey = keyof Form

// type needed as response id and org code arent actual form fields

export type FormTemplate = {
    name: string
    response: string
    automatic_response_id?: string
    org_code?: string
}
