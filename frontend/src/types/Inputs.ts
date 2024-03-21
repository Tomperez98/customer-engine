import {FormKey, FormTemplate} from './Forms'
import {TokenKey, TokenTemplate} from './Tokens'

export type InputName = FormKey | TokenKey

export type InputField = {
    name: InputName
    label: string
    editable?: boolean
    component: string
}

export type Template = FormTemplate | TokenTemplate
