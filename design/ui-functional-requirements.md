# UI Functional Requirements - Logger Manager Card

This document defines the core functionality and data requirements for the Logger Manager custom card implementation.

## 1. DATA TO PRESENT ON SCREEN
JG0: below I will make some changes an add comments I'll preceeed all comments with "JGx:" where x is the number of my comment to aid in referencing
JG1: expectat the below I will use the terms log/logs and logger/loggers interchangably
JG2: brodly, data to present includes: 1. current default logger level, 2. logs presently being managed (i.e. logs whose levels we have set to something other than the default logger level), 3. loggers availible to set.
JG3: your structure below implies manaaged and not-currrently-managed loggers will be listed together.  They will not. I envision a list of currently managed logs and a seperate list of availible logs that will be filered based search text entered. 
JG4: based on JG3 above, I"m going to create seperate sections below for managed and not availible loggers. 

### Managed Logger Data (per logger)
- **Logger Name** (e.g., "homeassistant.components.mqtt")
- **Current Level** (DEBUG, INFO, WARNING, ERROR, CRITICAL, or NOTSET)
- **Effective Level** (what level is actually being used - might inherit from parent) JG5: not sure what this means, but I don't think its neede
- **Is Managed** (boolean - are we actively managing this logger's level?) JG6: not needed (see JG3 and JG4)
- **Category/Type** (component, integration, platform, core, custom, etc.) JG7: probably not needed. Logger name should provide this context

### Availible Logger Data (per logger)
- **Logger Name** (e.g., "homeassistant.components.mqtt")

### Summary/Status Data
- **Total Loggers Available** (e.g., "571 loggers discovered") JG8: nice to have
- **Managed Loggers Count** (e.g., "12 currently managed") JG9: nice to have
- **Cache Status** (last refreshed timestamp) JG10: not needed
- **Filter Results** (e.g., "Showing 23 of 571 loggers") JG11: nice to have

### Defult logger status (JG12: I'm adding this section)
- **Current default logger level**
- **Is default logger level managed (Y/N)** JG13: I want to add the ability to change default logger level (can call existing HA function..no new backend code)
- **Managed level timeout** JG14: More on this below, but if a user changes default log level, we will require they provide a "how long" value...after which we will revert to the "default default" level

### Search/Filter State JG15: applies only to list of availible loggers.  Managed logger list won't be long enough to benefire from search/filter
- **Current Filter Text** (what user typed in search)
- **Selected Category Filter** (all, components, integrations, etc.) JG15: hmm...perhaps 
- **Selected Level Filter** (all, or specific level) JG16: not applicable

## 2. FUNCTIONS USER CAN PERFORM

### Availible Logger Discovery & Navigation
- **Search Loggers** - Filter a list of availible loggers by logger name (text input)
- **Filter by Category** - Show only components/integrations/platforms/etc. JG16: probably not needed
- **Filter by Level** - Show only loggers at specific levels JG17: not applicable. we dont retrieve (and thus don't know) level of availible loggers
- **Refresh Discovery** - Manually refresh the logger cache JG18: probably not needed

### Availible Logger Management JG19: I removed "core" from this item's description as it is a loaded term
- **Pick multiple loggers** - Select one or more loggers from list of availble loggers to action
- **Set Log Level** - Change selected logger(s) to specific level (DEBUG/INFO/WARNING/ERROR/CRITICAL). Setting all selected loggers to same level is acceptable functionality.
- **Reset to Default** - Remove our management, let logger return to inherited/default behavior JG20: availible loggers by definition are not managed, which means there is no level reset.  This functionality will be performed on seperately listed managed loggers
- **Add to Managed** - Start actively managing a previously unmanaged logger JG21: the act of setting the log level makes it a managed logger. So this functionality is not distinct from set log level.

### Managed Logger Management
- **Set log level** - change the level of a managed logger.  Changing level to defult log level removes the logger from the list of managed loggers

### Bulk Operations (v1 scope TBD)
- **Select Multiple managed loggers** - Checkbox selection of multiple loggers
- **Bulk Level Change** - Set same level for multiple loggers (both availible and managed) at once
- **Bulk Reset** - Remove management from multiple loggers JG22: not really different than setting level to default
- **Set survive restart - managed loggers** - specify if level of managed loggers should persist (or revert to defult) after HA restart

### (new) Defult logger level
- **Set default logger level** - Set default logger level
- **Set default logger revert timeout** -- specify the period of time (minutes? seconds?) after which the default logger will revert to "default default" level.  JG23: should we enforce an upper limit?
- **Set survive restart - default logger** -- specify if specificed defauly logger level should survive restart JG24: this might be too dangerout.  If we allow it, user needs to be warned.

### View Management JG25: I don't think any of this is needed
- **Sort Loggers** - By name, level, category, managed status
- **Toggle Managed Only** - Show only loggers we're actively managing
- **Clear Filters** - Reset all search/filter criteria

## QUESTIONS FOR ALIGNMENT
JG25: I preceed answer below with "A:"
### Data Questions:
1. **Parent Logger Relationships** - Should we show if a logger inherits from a parent? (e.g., "homeassistant.components.mqtt.light" inherits from "homeassistant.components.mqtt")
A: No. This should be evident in the name of the logger (and if its not, we won't know either)
2. **Level History** - Should we show when/how a level was last changed? Or keep v1 stateless?
A: not needed 
3. **Default Levels** - Should we show what the "default" level would be if we reset management?
A: good question.  The this should be the default logger level before we touch anything. I believe we've proven we can retrieve this, which we should do on startup.
### Function Questions:
1. **Bulk Operations in v1** - Include basic bulk operations or defer to v2?
A: I think so, but we can descope from MVP version if it proves complex
2. **Favorites/Pinning** - Allow users to "pin" frequently used loggers to top of list?
A: Def not in v1 buy def keep on list for future
3. **Level Inheritance** - If user sets "homeassistant.components" to DEBUG, should we warn it affects all child loggers?
A: User makes selecction at individual logger level, so I'm not sure how this would work
### UI/UX Questions:
1. **Managed vs Available** - Two separate views/tabs, or single view with toggle?
A: per above two seperate lists.
2. **Confirmation Dialogs** - Confirm level changes, or make them immediate?
A: TBD
3. **Undo/Reset** - Simple "reset to default" or more sophisticated undo?
A: consider including a "All to default" button and perhaps an "All to default in: (time period)"
## OTHER THINGS TO NAIL UP FRONT

### Technical Architecture
- **WebSocket Command Structure** - Standardize the message format
- **Error Handling Strategy** - How do we handle/display errors to user?
- **State Management** - Does card maintain state or always fetch fresh?

### Card Configuration
- **Default View** - What does user see on first load?
- **Configurable Options** - What can users customize in card config?
- **Responsive Design** - How does layout adapt to different screen sizes?

### Integration Patterns
- **Dashboard Auto-Creation** - Do we auto-create the dashboard or require manual setup?
- **Card Registration** - How does the custom card get registered/discovered?
- **Resource Loading** - How do we ensure card JS/CSS loads properly?

---

**Status:** Ready for review and inline comments. Critical questions need resolution before implementation begins.