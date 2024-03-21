export enum TokenKeys {
    access_token = 'Token de acceso (Access token)',
    user_token = 'Token de usuario (User token)',
}

export type TokenTemplate = {
    access_token: string
    user_token: string
}

export type TokenKey = keyof TokenTemplate

export interface Token extends TokenTemplate {
    org_code: string
}
