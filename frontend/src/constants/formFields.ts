import {FormKey, FormKeys} from '@/types/Forms'

type InputField = {
    name: FormKey
    label: string
    editable?: boolean
    component?: string
}

export const INPUT_FIELDS: InputField[] = [
    {
        name: 'name',
        label: FormKeys['name'],
        editable: true,
        component: 'input',
    },
    {
        name: 'examples',
        label: FormKeys['examples'],
        editable: true,
        component: 'list',
    },
    {
        name: 'response',
        label: FormKeys['response'],
        editable: true,
        component: 'textarea',
    },
]

export const FORM_TEMPLATE = {
    name: '',
    examples: [''],
    response: '',
}
