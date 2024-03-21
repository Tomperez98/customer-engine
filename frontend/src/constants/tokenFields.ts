import {InputField} from '@/types/Inputs'
import {TokenKeys} from '@/types/Tokens'

export const TOKEN_FIELDS: InputField[] = [
    {
        name: 'access_token',
        label: TokenKeys['access_token'],
        editable: true,
        component: 'input',
    },
    {
        name: 'user_token',
        label: TokenKeys['user_token'],
        editable: true,
        component: 'input',
    },
]

export const TOKEN_TEMPLATE = {
    access_token: '',
    user_token: '',
}
