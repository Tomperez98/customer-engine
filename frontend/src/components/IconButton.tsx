import classNames from 'classnames'
import {motion} from 'framer-motion'
import {Tooltip} from 'react-tooltip'
import {v4 as uuidv4} from 'uuid'

interface IconButtonProps {
    Icon: any
    onClick: () => void
    disabled?: boolean
    fill?: string
    size?: string
    tooltip?: string
}

const IconButton = ({
    disabled,
    fill,
    Icon,
    size,
    onClick,
    tooltip,
}: IconButtonProps) => {
    const animationProps = disabled
        ? {}
        : {
              whileHover: {scale: 1.1},
              whileTap: {scale: 0.9},
          }
    const tooltipId = uuidv4()
    return (
        <>
            {tooltip && (
                <Tooltip
                    className='!bg-neutral-800 !opacity-100'
                    id={tooltipId}
                />
            )}
            <motion.button
                data-tooltip-id={tooltipId}
                data-tooltip-content={tooltip}
                data-tooltip-place='top'
                className={classNames(
                    fill ||
                        'text-neutral-800 hover:text-cyan-400 disabled:text-slate-200',
                    size || 'text-sm'
                )}
                disabled={disabled}
                onClick={onClick}
                {...animationProps}>
                <Icon />
            </motion.button>
        </>
    )
}

export default IconButton
